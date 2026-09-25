import random
from enum import StrEnum

from django.db import transaction

from .models import SEAT_LETTERS, SEAT_ROWS, Flight, Ticket


class TicketError(Exception):
    """Ошибка бизнес-логики, текст которой можно показать пользователю."""


class PurchaseOutcome(StrEnum):
    CREATED = "created"
    RESTORED = "restored"
    ALREADY_OWNED = "already_owned"


def pick_free_seat(flight: Flight) -> str:
    taken = set(
        flight.tickets.filter(status=Ticket.Status.CONFIRMED).values_list("seat", flat=True)
    )
    free = [f"{row}{letter}" for row in SEAT_ROWS for letter in SEAT_LETTERS]
    free = [seat for seat in free if seat not in taken]
    if not free:
        raise TicketError("На этот рейс мест больше нет. Даже самых дорогих.")
    return random.choice(free)


@transaction.atomic
def purchase_ticket(passenger, flight: Flight) -> tuple[Ticket, PurchaseOutcome]:
    if flight.is_departed:
        raise TicketError("Этот рейс уже улетел — билеты больше не продаются.")

    ticket, created = Ticket.objects.select_for_update().get_or_create(
        flight=flight,
        passenger=passenger,
        defaults={"seat": lambda: pick_free_seat(flight), "price": flight.price},
    )
    if created:
        return ticket, PurchaseOutcome.CREATED
    if ticket.is_active:
        return ticket, PurchaseOutcome.ALREADY_OWNED

    ticket.status = Ticket.Status.CONFIRMED
    ticket.seat = pick_free_seat(flight)
    ticket.price = flight.price
    ticket.save(update_fields=["status", "seat", "price", "updated_at"])
    return ticket, PurchaseOutcome.RESTORED


def cancel_ticket(ticket: Ticket) -> None:
    if not ticket.is_active:
        raise TicketError("Этот билет уже отменён.")
    if ticket.flight.is_departed:
        raise TicketError("Самолёт уже в воздухе — отменить билет нельзя.")
    ticket.status = Ticket.Status.CANCELLED
    ticket.save(update_fields=["status", "updated_at"])
