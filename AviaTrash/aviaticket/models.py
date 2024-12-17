from django.db import models

class Flight(models.Model):
    flight_from = models.CharField(max_length=50, verbose_name='Откуда')
    flight_to = models.CharField(max_length=50, verbose_name='Куда')
    airline = models.CharField(max_length=100, verbose_name='Авиакомпания')
    time_in_flight = models.DateTimeField(verbose_name='Время в пути')
    day_of_departure = models.DateField(verbose_name='Дата вылета')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    amount_of_transfers = models.IntegerField(blank=True, null=True, verbose_name='Количество пересадок')

    def __str__(self):
        return f"Рейс {self.airline}: {self.flight_from} → {self.flight_to}, {self.day_of_departure}, {self.price} ₽"


class Ticket(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='tickets')
    passenger_first_name = models.CharField(max_length=100, verbose_name='Имя пассажира')
    passenger_last_name = models.CharField(max_length=100, verbose_name='Фамилия пассажира')
    passenger_email = models.EmailField(verbose_name='Электронная почта пассажира')
    passenger_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон пассажира')

    status_choices = [
        ('booked', 'Забронирован'),
        ('confirmed', 'Подтвержден'),
        ('cancelled', 'Отменен'),
        ('completed', 'Завершен'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='booked', verbose_name='Статус билета')

    payment_status_choices = [
        ('paid', 'Оплачен'),
        ('unpaid', 'Не оплачен'),
        ('pending', 'Ожидает оплаты'),
    ]
    payment_status = models.CharField(max_length=20, choices=payment_status_choices, default='unpaid', verbose_name='Статус оплаты')

    booking_reference = models.CharField(max_length=50, unique=True, verbose_name='Номер бронирования')
    booking_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата бронирования')

    def __str__(self):
        return f"Билет на рейс {self.flight.airline}: {self.flight.flight_from} → {self.flight.flight_to}, {self.flight.day_of_departure}"
