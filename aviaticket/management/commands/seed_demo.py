import random
from datetime import date, datetime, time, timedelta
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from aviaticket.models import Airline, City, Flight, Ticket
from aviaticket.services import cancel_ticket, purchase_ticket

SEED_DIR = Path(__file__).resolve().parents[2] / "seed"
HORIZON_DAYS = 30

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "aviatrash"

AIRLINES = [
    ("Aeroflot", "SU", "Россия", 1923),
    ("S7 Airlines", "S7", "Россия", 1992),
    ("Utair", "UT", "Россия", 1991),
    ("Pobeda", "DP", "Россия", 2014),
    ("Air France", "AF", "Франция", 1933),
    ("Lufthansa", "LH", "Германия", 1953),
    ("Emirates", "EK", "ОАЭ", 1985),
    ("ANA", "NH", "Япония", 1952),
    ("Turkish Airlines", "TK", "Турция", 1933),
    ("Pegasus Airlines", "PC", "Турция", 1990),
    ("Belavia", "B2", "Беларусь", 1996),
    ("British Airways", "BA", "Великобритания", 1974),
    ("Alitalia", "AZ", "Италия", 1946),
    ("KLM", "KL", "Нидерланды", 1919),
    ("Czech Airlines", "OK", "Чехия", 1923),
    ("Air Astana", "KC", "Казахстан", 2001),
    ("Finnair", "AY", "Финляндия", 1923),
]

CITIES = [
    ("Москва", "MOW", None),
    ("Новосибирск", "OVB", None),
    ("Казань", "KZN", None),
    ("Краснодар", "KRR", None),
    ("Омск", "OMS", None),
    ("Калуга", "KLF", None),
    ("Воронеж", "VOZ", None),
    ("Мурманск", "MMK", None),
    ("Ростов-на-Дону", "ROV", None),
    ("Уфа", "UFA", None),
    ("Калининград", "KGD", None),
    ("Челябинск", "CEK", None),
    ("Санкт-Петербург", "LED", "saint-petersburg.jpg"),
    ("Екатеринбург", "SVX", "yekaterinburg.jpg"),
    ("Самара", "KUF", "samara.jpg"),
    ("Сочи", "AER", "sochi.jpg"),
    ("Владивосток", "VVO", "vladivostok.jpg"),
    ("Париж", "PAR", "paris.jpg"),
    ("Берлин", "BER", "berlin.jpg"),
    ("Нью-Йорк", "NYC", "new-york.jpg"),
    ("Дубай", "DXB", "dubai.jpg"),
    ("Токио", "TYO", "tokyo.jpg"),
    ("Стамбул", "IST", "istanbul.jpg"),
    ("Анталия", "AYT", "antalya.jpg"),
    ("Минск", "MSQ", "minsk.jpg"),
    ("Лондон", "LON", "london.jpg"),
    ("Рим", "ROM", "rome.jpg"),
    ("Амстердам", "AMS", "amsterdam.jpg"),
    ("Прага", "PRG", "prague.jpg"),
    ("Астана", "NQZ", "astana.jpg"),
    ("Мюнхен", "MUC", "munich.jpg"),
    ("Хельсинки", "HEL", "helsinki.jpg"),
]

# Номер рейса, откуда, куда, минут в пути, пересадок, базовая цена.
ROUTES = [
    ("SU 1402", "MOW", "LED", 120, 0, 4_500),
    ("S7 2051", "OVB", "SVX", 210, 1, 5_300),
    ("UT 431", "KZN", "KUF", 110, 0, 2_900),
    ("DP 118", "KRR", "AER", 60, 0, 1_500),
    ("SU 1706", "OMS", "VVO", 465, 1, 9_800),
    ("AF 1845", "MOW", "PAR", 250, 0, 18_500),
    ("LH 1433", "LED", "BER", 225, 1, 16_200),
    ("SU 100", "MOW", "NYC", 630, 0, 48_200),
    ("EK 186", "SVX", "DXB", 350, 0, 32_700),
    ("NH 952", "VVO", "TYO", 210, 0, 22_400),
    ("TK 414", "MOW", "IST", 240, 0, 17_500),
    ("PC 571", "AER", "AYT", 135, 0, 12_000),
    ("B2 954", "KLF", "MSQ", 365, 0, 8_000),
    ("BA 233", "MOW", "LON", 440, 0, 21_500),
    ("AZ 547", "VOZ", "ROM", 520, 2, 17_500),
    ("KL 1398", "MMK", "AMS", 670, 0, 19_800),
    ("OK 921", "ROV", "PRG", 590, 0, 12_500),
    ("KC 342", "UFA", "NQZ", 240, 0, 14_800),
    ("LH 1447", "KGD", "MUC", 330, 0, 18_500),
    ("AY 712", "CEK", "HEL", 110, 0, 15_500),
]


class Command(BaseCommand):
    help = "Наполняет базу демо-данными: города, авиакомпании, расписание и демо-пользователь."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fresh",
            action="store_true",
            help="Удалить все рейсы и билеты перед генерацией нового расписания.",
        )

    @transaction.atomic
    def handle(self, *args, fresh: bool, **options):
        if fresh:
            Ticket.objects.all().delete()
            Flight.objects.all().delete()
            self.stdout.write("Старые рейсы и билеты удалены.")

        airlines = self.seed_airlines()
        cities = self.seed_cities()
        created_flights = self.seed_flights(airlines, cities, timezone.localdate())
        demo_created = self.seed_demo_user()

        upcoming = Flight.objects.upcoming().count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: авиакомпаний — {len(airlines)}, городов — {len(cities)}, "
                f"новых рейсов — {created_flights}, всего предстоящих — {upcoming}."
            )
        )
        if demo_created:
            self.stdout.write(
                self.style.SUCCESS(f"Демо-пользователь: {DEMO_USERNAME} / {DEMO_PASSWORD}")
            )

    def seed_airlines(self) -> dict[str, Airline]:
        airlines = {}
        for name, code, country, founded_year in AIRLINES:
            airline, _ = Airline.objects.update_or_create(
                code=code,
                defaults={"name": name, "country": country, "founded_year": founded_year},
            )
            airlines[code] = airline
        return airlines

    def seed_cities(self) -> dict[str, City]:
        cities = {}
        for name, code, photo in CITIES:
            city, _ = City.objects.update_or_create(code=code, defaults={"name": name})
            if photo and not (city.photo and default_storage.exists(city.photo.name)):
                self.attach_photo(city, photo)
            cities[code] = city
        return cities

    @staticmethod
    def attach_photo(city: City, filename: str) -> None:
        target = f"cities/{filename}"
        if default_storage.exists(target):
            city.photo.name = target
            city.save(update_fields=["photo"])
            return
        with (SEED_DIR / "cities" / filename).open("rb") as source:
            city.photo.save(filename, File(source), save=True)

    def seed_flights(
        self, airlines: dict[str, Airline], cities: dict[str, City], today: date
    ) -> int:
        existing = set(Flight.objects.values_list("slug", flat=True))
        new_flights = []
        for number, origin, destination, minutes, transfers, base_price in ROUTES:
            for departure_at, price in schedule(number, base_price, today):
                flight = Flight(
                    number=number,
                    airline=airlines[number.split()[0]],
                    origin=cities[origin],
                    destination=cities[destination],
                    departure_at=departure_at,
                    duration=timedelta(minutes=minutes),
                    transfers=transfers,
                    price=price,
                )
                flight.slug = flight.build_slug()
                if flight.slug not in existing:
                    new_flights.append(flight)
        Flight.objects.bulk_create(new_flights)
        return len(new_flights)

    def seed_demo_user(self) -> bool:
        user, created = get_user_model().objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={
                "email": "demo@aviatrash.local",
                "first_name": "Демо",
                "last_name": "Пассажиров",
            },
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save(update_fields=["password"])

        if not user.tickets.exists():
            tickets = [purchase_ticket(user, flight)[0] for flight in priciest_routes(limit=3)]
            if tickets:
                cancel_ticket(tickets[-1])
        return created


def priciest_routes(limit: int) -> list[Flight]:
    """Самые дорогие рейсы, но не больше одного на направление."""
    picked: dict[int, Flight] = {}
    for flight in Flight.objects.upcoming().order_by("-price"):
        picked.setdefault(flight.destination_id, flight)
        if len(picked) == limit:
            break
    return list(picked.values())


def schedule(number: str, base_price: int, today: date):
    """Детерминированное расписание: повторный запуск в тот же день не создаёт дублей."""
    rng = random.Random(number)
    period = rng.randint(5, 9)
    phase = rng.randrange(period)
    departure_time = time(rng.randint(6, 22), rng.randrange(0, 60, 5))

    for offset in range(1, HORIZON_DAYS + 1):
        day = today + timedelta(days=offset)
        if (day.toordinal() + phase) % period:
            continue
        price_rng = random.Random(f"{number}:{day.isoformat()}")
        price = round(base_price * price_rng.uniform(0.85, 1.45), -2)
        yield timezone.make_aware(datetime.combine(day, departure_time)), int(price)
