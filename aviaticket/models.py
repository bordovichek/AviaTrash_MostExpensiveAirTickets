import secrets
from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models import F, Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

SEAT_ROWS = range(1, 31)
SEAT_LETTERS = "ABCDEF"
SEATS_PER_FLIGHT = len(SEAT_ROWS) * len(SEAT_LETTERS)

# Без 0/O и 1/I, чтобы номер брони нельзя было прочитать двояко.
PNR_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
PNR_LENGTH = 6


def generate_pnr() -> str:
    return "".join(secrets.choice(PNR_ALPHABET) for _ in range(PNR_LENGTH))


def current_year() -> int:
    return timezone.localdate().year


class City(models.Model):
    name = models.CharField("название", max_length=64, unique=True)
    code = models.CharField(
        "код IATA",
        max_length=3,
        unique=True,
        validators=[RegexValidator(r"^[A-Z]{3}$", "Три заглавные латинские буквы, например MOW.")],
    )
    photo = models.ImageField("фотография", upload_to="cities/", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "город"
        verbose_name_plural = "города"

    def __str__(self) -> str:
        return self.name


class Airline(models.Model):
    name = models.CharField("название", max_length=100, unique=True)
    code = models.CharField(
        "код IATA",
        max_length=2,
        unique=True,
        validators=[
            RegexValidator(r"^[A-Z0-9]{2}$", "Две заглавные буквы или цифры, например SU.")
        ],
    )
    country = models.CharField("страна", max_length=100)
    founded_year = models.PositiveSmallIntegerField(
        "год основания",
        validators=[MinValueValidator(1909), MaxValueValidator(current_year)],
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "авиакомпания"
        verbose_name_plural = "авиакомпании"

    def __str__(self) -> str:
        return self.name


class FlightQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(departure_at__gt=timezone.now())

    def with_related(self):
        return self.select_related("airline", "origin", "destination")


class Flight(models.Model):
    number = models.CharField("номер рейса", max_length=8, help_text="Например, SU 1402")
    airline = models.ForeignKey(
        Airline, on_delete=models.PROTECT, related_name="flights", verbose_name="авиакомпания"
    )
    origin = models.ForeignKey(
        City, on_delete=models.PROTECT, related_name="departures", verbose_name="откуда"
    )
    destination = models.ForeignKey(
        City, on_delete=models.PROTECT, related_name="arrivals", verbose_name="куда"
    )
    departure_at = models.DateTimeField("вылет")
    duration = models.DurationField("время в пути", help_text="Формат: ЧЧ:ММ:СС")
    transfers = models.PositiveSmallIntegerField("пересадки", default=0)
    price = models.PositiveIntegerField("цена, ₽", validators=[MinValueValidator(1)])
    slug = models.SlugField("слаг", max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField("создан", auto_now_add=True)

    objects = FlightQuerySet.as_manager()

    class Meta:
        ordering = ["departure_at"]
        verbose_name = "рейс"
        verbose_name_plural = "рейсы"
        constraints = [
            models.CheckConstraint(
                condition=~Q(origin=F("destination")), name="flight_origin_differs_from_destination"
            ),
            models.CheckConstraint(
                condition=Q(duration__gt=timedelta(0)), name="flight_duration_positive"
            ),
        ]

    def __str__(self) -> str:
        departure = timezone.localtime(self.departure_at)
        return f"{self.number} {self.origin} → {self.destination}, {departure:%d.%m.%Y %H:%M}"

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = self.build_slug()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("aviaticket:flight_detail", args=[self.slug])

    def build_slug(self) -> str:
        return slugify(f"{self.number}-{timezone.localtime(self.departure_at):%Y-%m-%d}")

    def clean(self) -> None:
        if self.origin_id and self.origin_id == self.destination_id:
            raise ValidationError(
                {"destination": "Город прилёта должен отличаться от города вылета."}
            )
        if self.duration is not None and self.duration <= timedelta(0):
            raise ValidationError({"duration": "Время в пути должно быть больше нуля."})
        if self.number and self.departure_at:
            duplicate = Flight.objects.filter(slug=self.build_slug()).exclude(pk=self.pk)
            if duplicate.exists():
                raise ValidationError("Рейс с таким номером в этот день уже есть.")

    @property
    def arrival_at(self) -> datetime:
        return self.departure_at + self.duration

    @property
    def is_departed(self) -> bool:
        return self.departure_at <= timezone.now()


class Ticket(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Оформлен"
        CANCELLED = "cancelled", "Отменён"

    flight = models.ForeignKey(
        Flight, on_delete=models.PROTECT, related_name="tickets", verbose_name="рейс"
    )
    passenger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name="пассажир",
    )
    status = models.CharField("статус", max_length=16, choices=Status, default=Status.CONFIRMED)
    pnr = models.CharField(
        "номер бронирования",
        max_length=PNR_LENGTH,
        unique=True,
        default=generate_pnr,
        editable=False,
    )
    seat = models.CharField("место", max_length=4)
    price = models.PositiveIntegerField("стоимость, ₽", help_text="Цена на момент покупки")
    created_at = models.DateTimeField("оформлен", auto_now_add=True)
    updated_at = models.DateTimeField("изменён", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "билет"
        verbose_name_plural = "билеты"
        constraints = [
            models.UniqueConstraint(
                fields=["flight", "passenger"], name="one_ticket_per_passenger_per_flight"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.pnr} · {self.flight}"

    def get_absolute_url(self) -> str:
        return reverse("aviaticket:ticket_detail", args=[self.pnr])

    @property
    def is_active(self) -> bool:
        return self.status == self.Status.CONFIRMED

    @property
    def can_be_cancelled(self) -> bool:
        return self.is_active and not self.flight.is_departed
