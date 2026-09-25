from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import FlightSearchForm
from .models import SEATS_PER_FLIGHT, Flight, Ticket
from .services import PurchaseOutcome, TicketError, cancel_ticket, purchase_ticket


class FlightListView(ListView):
    template_name = "aviaticket/flight_list.html"
    context_object_name = "flights"
    paginate_by = 12

    def get_queryset(self):
        self.form = FlightSearchForm(self.request.GET or None)
        return self.form.filter(Flight.objects.upcoming().with_related())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context["page_obj"]
        context.update(
            form=self.form,
            max_price=self.object_list.aggregate(value=Max("price"))["value"],
            page_range=page.paginator.get_elided_page_range(page.number, on_each_side=1, on_ends=1),
        )
        return context


class FlightDetailView(DetailView):
    template_name = "aviaticket/flight_detail.html"
    queryset = Flight.objects.with_related()

    def get_context_data(self, **kwargs):
        flight = self.object
        user = self.request.user
        sold = flight.tickets.filter(status=Ticket.Status.CONFIRMED).count()
        return super().get_context_data(
            ticket=flight.tickets.filter(passenger=user).first() if user.is_authenticated else None,
            seats_left=SEATS_PER_FLIGHT - sold,
            other_dates=(
                Flight.objects.upcoming()
                .filter(origin=flight.origin, destination=flight.destination)
                .exclude(pk=flight.pk)
                .select_related("airline")[:4]
            ),
            **kwargs,
        )


class BuyTicketView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def handle_no_permission(self):
        flight = get_object_or_404(Flight, slug=self.kwargs["slug"])
        return redirect_to_login(flight.get_absolute_url(), self.get_login_url())

    def post(self, request, slug):
        flight = get_object_or_404(Flight, slug=slug)
        try:
            ticket, outcome = purchase_ticket(request.user, flight)
        except TicketError as error:
            messages.error(request, str(error))
            return redirect(flight)

        match outcome:
            case PurchaseOutcome.CREATED:
                messages.success(request, "Билет оформлен. Кошелёк плачет, а вы летите!")
            case PurchaseOutcome.RESTORED:
                messages.success(request, "Билет снова активен — место забронировано заново.")
            case PurchaseOutcome.ALREADY_OWNED:
                messages.info(request, "У вас уже есть билет на этот рейс.")
        return redirect(ticket)


class PassengerTicketsMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Ticket.objects.filter(passenger=self.request.user).select_related(
            "flight__airline", "flight__origin", "flight__destination"
        )


class TicketListView(PassengerTicketsMixin, ListView):
    template_name = "aviaticket/ticket_list.html"
    context_object_name = "tickets"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        upcoming, past, cancelled = [], [], []
        for ticket in self.object_list:
            if not ticket.is_active:
                cancelled.append(ticket)
            elif ticket.flight.departure_at > now:
                upcoming.append(ticket)
            else:
                past.append(ticket)
        upcoming.sort(key=lambda t: t.flight.departure_at)
        context["sections"] = [
            ("Предстоящие полёты", upcoming),
            ("Уже слетали", past),
            ("Отменённые", cancelled),
        ]
        return context


class TicketDetailView(PassengerTicketsMixin, DetailView):
    template_name = "aviaticket/ticket_detail.html"
    slug_field = "pnr"
    slug_url_kwarg = "pnr"


class CancelTicketView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pnr):
        ticket = get_object_or_404(
            Ticket.objects.select_related("flight"), pnr=pnr, passenger=request.user
        )
        try:
            cancel_ticket(ticket)
        except TicketError as error:
            messages.error(request, str(error))
        else:
            messages.success(request, "Билет отменён. Деньги вернутся… когда-нибудь.")
        return redirect(ticket)
