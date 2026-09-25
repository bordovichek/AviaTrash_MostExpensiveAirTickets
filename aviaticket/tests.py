import shutil
import tempfile
from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import PNR_ALPHABET, Airline, City, Flight, Ticket, generate_pnr
from .services import PurchaseOutcome, TicketError, cancel_ticket, purchase_ticket
from .templatetags.avia import duration, plural_ru, rub, transfers

User = get_user_model()


class FlightFactoryMixin:
    @classmethod
    def setUpTestData(cls):
        cls.airline = Airline.objects.create(
            name="Aeroflot", code="SU", country="Россия", founded_year=1923
        )
        cls.moscow = City.objects.create(name="Москва", code="MOW")
        cls.paris = City.objects.create(name="Париж", code="PAR")
        cls.tokyo = City.objects.create(name="Токио", code="TYO")
        cls.user = User.objects.create_user("ivan", "ivan@example.com", "Secret-pass-123")
        cls.other = User.objects.create_user("petr", "petr@example.com", "Secret-pass-123")

    @classmethod
    def make_flight(cls, *, days=3, price=10_000, destination=None, number="SU 100", **extra):
        return Flight.objects.create(
            number=number,
            airline=cls.airline,
            origin=cls.moscow,
            destination=destination or cls.paris,
            departure_at=timezone.now() + timedelta(days=days),
            duration=timedelta(hours=4, minutes=10),
            price=price,
            **extra,
        )


class FlightModelTests(FlightFactoryMixin, TestCase):
    def test_slug_is_built_from_number_and_local_date(self):
        flight = self.make_flight()
        local_date = timezone.localtime(flight.departure_at).date()
        self.assertEqual(flight.slug, f"su-100-{local_date:%Y-%m-%d}")

    def test_arrival_is_departure_plus_duration(self):
        flight = self.make_flight()
        self.assertEqual(flight.arrival_at - flight.departure_at, timedelta(hours=4, minutes=10))

    def test_clean_rejects_same_origin_and_destination(self):
        flight = self.make_flight()
        flight.destination = flight.origin
        with self.assertRaises(ValidationError):
            flight.clean()

    def test_clean_rejects_duplicate_number_on_same_day(self):
        existing = self.make_flight()
        duplicate = Flight(
            number=existing.number,
            airline=self.airline,
            origin=self.moscow,
            destination=self.tokyo,
            departure_at=existing.departure_at,
            duration=timedelta(hours=1),
            price=1,
        )
        with self.assertRaises(ValidationError):
            duplicate.clean()

    def test_upcoming_hides_departed_flights(self):
        future = self.make_flight(days=2)
        self.make_flight(days=-2, number="SU 200")
        self.assertQuerySetEqual(Flight.objects.upcoming(), [future])

    def test_generate_pnr_format(self):
        pnr = generate_pnr()
        self.assertEqual(len(pnr), 6)
        self.assertTrue(set(pnr) <= set(PNR_ALPHABET))


class PurchaseServiceTests(FlightFactoryMixin, TestCase):
    def test_purchase_creates_ticket_with_price_snapshot(self):
        flight = self.make_flight(price=12_345)
        ticket, outcome = purchase_ticket(self.user, flight)

        self.assertEqual(outcome, PurchaseOutcome.CREATED)
        self.assertEqual(ticket.price, 12_345)
        self.assertEqual(ticket.status, Ticket.Status.CONFIRMED)
        self.assertRegex(ticket.seat, r"^\d{1,2}[A-F]$")

    def test_second_purchase_does_not_duplicate(self):
        flight = self.make_flight()
        first, _ = purchase_ticket(self.user, flight)
        second, outcome = purchase_ticket(self.user, flight)

        self.assertEqual(outcome, PurchaseOutcome.ALREADY_OWNED)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_cancelled_ticket_is_restored(self):
        flight = self.make_flight()
        ticket, _ = purchase_ticket(self.user, flight)
        cancel_ticket(ticket)

        restored, outcome = purchase_ticket(self.user, flight)

        self.assertEqual(outcome, PurchaseOutcome.RESTORED)
        self.assertEqual(restored.pk, ticket.pk)
        self.assertEqual(restored.status, Ticket.Status.CONFIRMED)

    def test_cannot_buy_departed_flight(self):
        flight = self.make_flight(days=-1)
        with self.assertRaises(TicketError):
            purchase_ticket(self.user, flight)

    def test_cannot_cancel_twice(self):
        ticket, _ = purchase_ticket(self.user, self.make_flight())
        cancel_ticket(ticket)
        with self.assertRaises(TicketError):
            cancel_ticket(ticket)


class FlightListViewTests(FlightFactoryMixin, TestCase):
    url = reverse("aviaticket:flight_list")

    def test_default_sort_is_most_expensive_first(self):
        cheap = self.make_flight(price=1_000, number="SU 1")
        pricey = self.make_flight(price=90_000, number="SU 2")

        response = self.client.get(self.url)

        self.assertEqual(list(response.context["flights"]), [pricey, cheap])
        self.assertEqual(response.context["max_price"], 90_000)
        self.assertContains(response, "Дороже всех", count=1)

    def test_departed_flights_are_hidden(self):
        self.make_flight(days=-1)
        response = self.client.get(self.url)
        self.assertEqual(response.context["paginator"].count, 0)
        self.assertContains(response, "Ничего не нашлось")

    def test_filters_by_destination_and_date(self):
        tokyo = self.make_flight(destination=self.tokyo, days=10, number="SU 7")
        self.make_flight(destination=self.paris, days=10, number="SU 8")
        self.make_flight(destination=self.tokyo, days=1, number="SU 9")

        date_from = timezone.localdate() + timedelta(days=5)
        response = self.client.get(
            self.url, {"destination": self.tokyo.pk, "date_from": date_from.isoformat()}
        )

        self.assertEqual(list(response.context["flights"]), [tokyo])

    def test_sort_by_price_ascending(self):
        pricey = self.make_flight(price=90_000, number="SU 1")
        cheap = self.make_flight(price=1_000, number="SU 2")
        response = self.client.get(self.url, {"sort": "price_asc"})
        self.assertEqual(list(response.context["flights"]), [cheap, pricey])

    def test_pagination_keeps_filters_in_links(self):
        for index in range(13):
            self.make_flight(number=f"SU {index}")
        response = self.client.get(self.url, {"sort": "price_asc"})
        self.assertContains(response, "?sort=price_asc&amp;page=2")


class FlightDetailViewTests(FlightFactoryMixin, TestCase):
    def test_anonymous_sees_login_button(self):
        flight = self.make_flight()
        response = self.client.get(flight.get_absolute_url())
        self.assertContains(response, "Войти и купить")

    def test_owner_sees_link_to_boarding_pass(self):
        flight = self.make_flight()
        ticket, _ = purchase_ticket(self.user, flight)
        self.client.force_login(self.user)

        response = self.client.get(flight.get_absolute_url())

        self.assertContains(response, ticket.get_absolute_url())

    def test_unknown_flight_is_404(self):
        response = self.client.get(reverse("aviaticket:flight_detail", args=["nope"]))
        self.assertEqual(response.status_code, 404)


class TicketViewsTests(FlightFactoryMixin, TestCase):
    def test_anonymous_buy_redirects_to_login_with_flight_as_next(self):
        flight = self.make_flight()
        response = self.client.post(reverse("aviaticket:buy_ticket", args=[flight.slug]))
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={flight.get_absolute_url()}",
            fetch_redirect_response=False,
        )

    def test_buy_redirects_to_boarding_pass(self):
        flight = self.make_flight()
        self.client.force_login(self.user)

        response = self.client.post(reverse("aviaticket:buy_ticket", args=[flight.slug]))

        ticket = Ticket.objects.get()
        self.assertRedirects(response, ticket.get_absolute_url())

    def test_buy_is_post_only(self):
        flight = self.make_flight()
        self.client.force_login(self.user)
        response = self.client.get(reverse("aviaticket:buy_ticket", args=[flight.slug]))
        self.assertEqual(response.status_code, 405)

    def test_foreign_ticket_is_hidden(self):
        ticket, _ = purchase_ticket(self.other, self.make_flight())
        self.client.force_login(self.user)

        detail = self.client.get(ticket.get_absolute_url())
        cancel = self.client.post(reverse("aviaticket:cancel_ticket", args=[ticket.pnr]))

        self.assertEqual(detail.status_code, 404)
        self.assertEqual(cancel.status_code, 404)
        ticket.refresh_from_db()
        self.assertTrue(ticket.is_active)

    def test_cancel_ticket(self):
        ticket, _ = purchase_ticket(self.user, self.make_flight())
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("aviaticket:cancel_ticket", args=[ticket.pnr]), follow=True
        )

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, Ticket.Status.CANCELLED)
        self.assertContains(response, "Билет отменён")

    def test_ticket_list_groups_by_state(self):
        upcoming, _ = purchase_ticket(self.user, self.make_flight(number="SU 1"))
        cancelled, _ = purchase_ticket(self.user, self.make_flight(number="SU 2"))
        cancel_ticket(cancelled)
        self.client.force_login(self.user)

        response = self.client.get(reverse("aviaticket:ticket_list"))

        sections = dict(response.context["sections"])
        self.assertEqual(sections["Предстоящие полёты"], [upcoming])
        self.assertEqual(sections["Отменённые"], [cancelled])


class TemplateFiltersTests(TestCase):
    def test_rub(self):
        self.assertEqual(rub(1234567), "1 234 567 ₽")

    def test_plural_ru(self):
        forms = "рейс,рейса,рейсов"
        cases = {1: "рейс", 3: "рейса", 5: "рейсов", 11: "рейсов", 21: "рейс", 112: "рейсов"}
        for number, expected in cases.items():
            with self.subTest(number=number):
                self.assertEqual(plural_ru(number, forms), expected)

    def test_duration(self):
        self.assertEqual(duration(timedelta(hours=2, minutes=5)), "2 ч 05 мин")
        self.assertEqual(duration(timedelta(minutes=45)), "45 мин")

    def test_transfers(self):
        self.assertEqual(transfers(0), "Прямой рейс")
        self.assertEqual(transfers(2), "2 пересадки")


class SeedDemoCommandTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)

    def test_seed_is_idempotent(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            call_command("seed_demo", stdout=StringIO())
            flights = Flight.objects.count()
            call_command("seed_demo", stdout=StringIO())

        self.assertGreater(flights, 0)
        self.assertEqual(Flight.objects.count(), flights)
        self.assertTrue(City.objects.get(code="PAR").photo)
        demo = User.objects.get(username="demo")
        self.assertTrue(demo.check_password("aviatrash"))
        self.assertEqual(demo.tickets.count(), 3)
