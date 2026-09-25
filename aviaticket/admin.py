from django.contrib import admin
from django.utils.html import format_html

from .models import Airline, City, Flight, Ticket


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "photo_preview")
    search_fields = ("name", "code")
    readonly_fields = ("photo_preview",)

    @admin.display(description="превью")
    def photo_preview(self, city: City) -> str:
        if not city.photo:
            return "—"
        return format_html(
            '<img src="{}" alt="" style="height:48px;border-radius:6px;object-fit:cover">',
            city.photo.url,
        )


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "country", "founded_year")
    search_fields = ("name", "code", "country")


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    fields = ("pnr", "passenger", "seat", "price", "status")
    readonly_fields = ("pnr",)
    autocomplete_fields = ("passenger",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "origin",
        "destination",
        "departure_at",
        "airline",
        "price",
        "transfers",
    )
    list_filter = ("airline", "origin", "destination")
    list_select_related = ("airline", "origin", "destination")
    search_fields = ("number", "origin__name", "destination__name", "airline__name")
    autocomplete_fields = ("airline", "origin", "destination")
    readonly_fields = ("slug", "created_at")
    date_hierarchy = "departure_at"
    inlines = (TicketInline,)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("pnr", "passenger", "flight", "seat", "price", "status", "created_at")
    list_filter = ("status", "flight__airline")
    list_select_related = ("passenger", "flight__origin", "flight__destination")
    search_fields = ("pnr", "passenger__username", "passenger__email", "flight__number")
    autocomplete_fields = ("flight", "passenger")
    readonly_fields = ("pnr", "created_at", "updated_at")
