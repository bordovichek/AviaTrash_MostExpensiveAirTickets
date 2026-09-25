from django import forms
from django.db import models
from django.utils import timezone

from .models import City


class FlightSort(models.TextChoices):
    PRICE_DESC = "price_desc", "Сначала дорогие"
    PRICE_ASC = "price_asc", "Сначала дешёвые"
    DEPARTURE = "departure", "По дате вылета"
    DURATION = "duration", "Подольше в полёте"


FLIGHT_ORDERING = {
    FlightSort.PRICE_DESC: ("-price", "departure_at"),
    FlightSort.PRICE_ASC: ("price", "departure_at"),
    FlightSort.DEPARTURE: ("departure_at",),
    FlightSort.DURATION: ("-duration", "departure_at"),
}


class FlightSearchForm(forms.Form):
    origin = forms.ModelChoiceField(
        label="Откуда", queryset=City.objects.none(), required=False, empty_label="Любой город"
    )
    destination = forms.ModelChoiceField(
        label="Куда", queryset=City.objects.none(), required=False, empty_label="Куда угодно"
    )
    date_from = forms.DateField(
        label="Вылет с",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    sort = forms.ChoiceField(label="Сортировка", choices=FlightSort.choices, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = timezone.now()
        self.fields["origin"].queryset = City.objects.filter(
            departures__departure_at__gt=now
        ).distinct()
        self.fields["destination"].queryset = City.objects.filter(
            arrivals__departure_at__gt=now
        ).distinct()
        self.fields["date_from"].widget.attrs["min"] = timezone.localdate().isoformat()

    def filter(self, queryset):
        data = self.cleaned_data if self.is_bound and self.is_valid() else {}
        if origin := data.get("origin"):
            queryset = queryset.filter(origin=origin)
        if destination := data.get("destination"):
            queryset = queryset.filter(destination=destination)
        if date_from := data.get("date_from"):
            queryset = queryset.filter(departure_at__date__gte=date_from)
        sort = data.get("sort") or FlightSort.PRICE_DESC
        return queryset.order_by(*FLIGHT_ORDERING[sort])

    @property
    def is_filtered(self) -> bool:
        data = self.cleaned_data if self.is_bound and self.is_valid() else {}
        return any(data.get(name) for name in ("origin", "destination", "date_from"))
