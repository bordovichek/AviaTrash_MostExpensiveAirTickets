from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Flight(models.Model):
    flight_from = models.CharField(max_length=50, verbose_name='Откуда')
    flight_to = models.CharField(max_length=50, verbose_name='Куда')
    airline = models.ForeignKey('Airline', on_delete=models.CASCADE, related_name='airline', verbose_name='Авиакомпания')
    time_in_flight = models.DateTimeField(verbose_name='Время в пути')
    day_of_departure = models.DateField(verbose_name='Дата вылета')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    amount_of_transfers = models.IntegerField(blank=True, null=True, verbose_name='Количество пересадок')
    time_created = models.DateTimeField(auto_now=True, verbose_name='Время создания')

    def __str__(self):
        return f"Рейс {self.airline}: {self.flight_from} → {self.flight_to}, {self.day_of_departure}, {self.price} ₽"


class Ticket(models.Model):
    flight = models.OneToOneField('Flight', on_delete=models.CASCADE, related_name='flight_card')
    passenger = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='tickets', verbose_name='Пассажир')

    status_choices = [
        ('booked', 'Забронирован'),
        ('confirmed', 'Подтвержден'),
        ('cancelled', 'Отменен'),
        ('completed', 'Завершен'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='booked', verbose_name='Статус билета')

    # payment_status_choices = [
    #     ('paid', 'Оплачен'),
    #     ('unpaid', 'Не оплачен'),
    #     ('pending', 'Ожидает оплаты'),
    # ]
    # payment_status = models.CharField(max_length=20, choices=payment_status_choices, default='unpaid', verbose_name='Статус оплаты')

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