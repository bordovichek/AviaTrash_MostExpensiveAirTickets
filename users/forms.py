from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .models import User


class EmailUniqueMixin:
    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        duplicates = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("Пользователь с таким e-mail уже зарегистрирован.")
        return email


class RegisterForm(EmailUniqueMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")
        help_texts = {"username": "Латиница, цифры и символы @ . + - _"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name"):
            self.fields[name].required = True
        self.fields["first_name"].help_text = "Как в паспорте — впишем в посадочный талон."


class ProfileForm(EmailUniqueMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "birth_date")
        widgets = {
            "phone": forms.TextInput(attrs={"placeholder": "+7 999 123-45-67", "inputmode": "tel"}),
            "birth_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data["birth_date"]
        if birth_date and birth_date > timezone.localdate():
            raise forms.ValidationError("Дата рождения не может быть в будущем.")
        return birth_date
