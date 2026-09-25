from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q, Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, UpdateView

from aviaticket.models import Ticket

from .forms import ProfileForm, RegisterForm
from .models import User


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("aviaticket:flight_list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f"Добро пожаловать на борт, {self.object.display_name}!")
        return response


class LoginView(auth_views.LoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True


class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = ProfileForm
    template_name = "users/profile.html"
    context_object_name = "account"
    success_url = reverse_lazy("users:profile")
    success_message = "Данные профиля сохранены."

    def get_object(self, queryset=None):
        # Отдельная копия: невалидная форма не должна менять request.user в шапке.
        return User.objects.get(pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        confirmed = Q(status=Ticket.Status.CONFIRMED)
        stats = Ticket.objects.filter(passenger=self.request.user).aggregate(
            total=Count("pk"),
            upcoming=Count("pk", filter=confirmed & Q(flight__departure_at__gt=timezone.now())),
            spent=Sum("price", filter=confirmed, default=0),
        )
        return super().get_context_data(stats=stats, **kwargs)


class PasswordChangeView(SuccessMessageMixin, auth_views.PasswordChangeView):
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:profile")
    success_message = "Пароль изменён."
