from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify

def translit_to_eng(s: str) -> str:
    d = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
         'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'iy', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
         'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
         'ш': 'sh', 'щ': 'shch', 'ь': "", 'ы': 'y', 'ъ': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'}

    return "".join(map(lambda x: d[x] if d.get(x, False) else x, s.lower()))

class Flight(models.Model):
    flight_from = models.CharField(max_length=50, verbose_name='Откуда')
    flight_to = models.ForeignKey('CityWithPhoto', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Куда')
    airline = models.ForeignKey('Airline', on_delete=models.CASCADE, related_name='airline', verbose_name='Авиакомпания')
    time_in_flight = models.DateTimeField(verbose_name='Время в пути')
    day_of_departure = models.DateField(verbose_name='Дата вылета')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    amount_of_transfers = models.IntegerField(blank=True, null=True, verbose_name='Количество пересадок')
    time_created = models.DateTimeField(auto_now=True, verbose_name='Время создания')
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name='Слаг')

    def save(self, *args, **kwargs):
        if not self.slug:
            to = translit_to_eng(self.flight_to.city_name.replace(" ", "").replace("-", ""))
            from_ = translit_to_eng(self.flight_from.replace(" ", "").replace("-", ""))
            airline = self.airline.name.replace(" ", "").replace("-", "")
            self.slug = slugify(f"{to}_{from_}_{airline}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Рейс {self.airline}: {self.flight_from} → {self.flight_to.city_name}, {self.day_of_departure}, {self.price} ₽"



class Ticket(models.Model):
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE, related_name='tickets')
    passenger = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='tickets', verbose_name='Пассажир')

    status_choices = [
        ('booked', 'Забронирован'),
        ('confirmed', 'Подтвержден'),
        ('cancelled', 'Отменен'),
        ('completed', 'Завершен'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='booked', verbose_name='Статус билета')

    booking_reference = models.CharField(max_length=50, unique=True, verbose_name='Номер бронирования')
    booking_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата бронирования')

    def __str__(self):
        return f"Билет на рейс {self.flight.airline}: {self.flight.flight_from} → {self.flight.flight_to}, {self.flight.day_of_departure}"



class Airline(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название авиакомпании')
    country = models.CharField(max_length=100)
    founded_year = models.IntegerField(
        validators=[
            MinValueValidator(1910),
            MaxValueValidator(2023)
        ]
    )

    def __str__(self):
        return self.name


class CityWithPhoto(models.Model):
    city_name = models.CharField(
        max_length=55,
        unique=True,
        verbose_name="Название города"
    )
    photo = models.FileField(
        upload_to='media_photo_city',
        verbose_name="Фотография города"
    )

    def __str__(self):
        return self.city_name
