from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from .models import Flight, Ticket


class FlightListView(ListView):
    model = Flight
    template_name = 'aviaticket/ticket_list.html'
    context_object_name = 'page_obj'
    paginate_by = 13
    ordering = ['day_of_departure']

    def get_queryset(self):
        return Flight.objects.all().order_by('day_of_departure')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        flights = self.get_queryset()
        paginator = Paginator(flights, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class BuyTicketView(LoginRequiredMixin, View):
    """Покупка билета на рейс."""

    def post(self, request, slug):
        flight = get_object_or_404(Flight, slug=slug)
        ticket = Ticket.objects.filter(flight=flight, passenger=request.user, status='cancelled').first()
        if ticket:
            ticket.status = 'confirmed'
            ticket.save()
            messages.success(request, 'Вы успешно восстановили билет на этот рейс.')
        else:
            if Ticket.objects.filter(flight=flight, passenger=request.user, status='confirmed').exists():
                messages.error(request, 'Вы уже приобрели билет на этот рейс.')
            else:
                Ticket.objects.create(
                    flight=flight,
                    passenger=request.user,
                    status='confirmed',
                    booking_reference=f"REF-{flight.slug}-{request.user.id}"
                )
                messages.success(request, 'Вы успешно приобрели билет.')

        return redirect('ticket_ordered')


class TicketOrderedView(TemplateView):
    """Страница успешной покупки."""
    template_name = 'aviaticket/ticket_ordered.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'Поздравляем! Вы успешно приобрели билет.'
        return context


class TicketNotOrderedView(TemplateView):
    """Страница ошибки при покупке билета."""
    template_name = 'aviaticket/ticket_not_ordered.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'Ошибка. Покупка билета не удалась.'
        return context


class FlightDetailView(DetailView):
    model = Flight
    template_name = 'aviaticket/ticket_detail.html'
    context_object_name = 'flight'


class CancelTicketView(LoginRequiredMixin, View):
    """Отмена билета пользователем."""

    def post(self, request, ticket_id):
        # Получаем билет
        ticket = get_object_or_404(Ticket, id=ticket_id, passenger=request.user)

        # Если билет еще не отменен, меняем его статус на "cancelled"
        if ticket.status != 'cancelled':
            ticket.status = 'cancelled'
            ticket.save()
            messages.success(request, 'Билет успешно отменен.')
        else:
            messages.error(request, 'Этот билет уже отменен.')

        # Перенаправляем пользователя в личный кабинет
        return redirect('personal:profile')