from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    date_birth = models.DateTimeField(blank=True, null=True, verbose_name="Дата рождения")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")

    class Meta:
        db_table = 'auth_user'
