from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^\+?[\d\s()\-]{7,20}$",
    message="Введите телефон в формате +7 999 123-45-67.",
)


class User(AbstractUser):
    email = models.EmailField("e-mail", unique=True)
    phone = models.CharField("телефон", max_length=20, blank=True, validators=[phone_validator])
    birth_date = models.DateField("дата рождения", null=True, blank=True)

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    @property
    def display_name(self) -> str:
        return self.get_full_name() or self.username

    @property
    def initials(self) -> str:
        parts = [self.first_name, self.last_name] if self.first_name else [self.username]
        return "".join(part[0] for part in parts if part).upper()[:2]
