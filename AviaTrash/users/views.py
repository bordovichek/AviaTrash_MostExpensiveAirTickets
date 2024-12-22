from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from django.views.generic.edit import FormView, UpdateView
from .forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm
from django.contrib.auth.views import PasswordChangeView, LoginView

from aviaticket.models import Ticket


class RegisterUserView(FormView):
    template_name = 'users/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': "Авторизация"}

    def get_success_url(self):
        return reverse_lazy('list_tickets')



class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': "Профиль пользователя"}
    success_url = reverse_lazy('list_tickets')

    def get_success_url(self):
        return reverse_lazy('personal:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tickets'] = Ticket.objects.filter(passenger=self.request.user).order_by('-booking_date')
        return context


# Смена пароля
class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy("personal:password_change_done")
    template_name = "users/password_change_form.html"
    form_class = UserPasswordChangeForm
