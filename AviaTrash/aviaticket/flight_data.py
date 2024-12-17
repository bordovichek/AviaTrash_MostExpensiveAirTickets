# ну да я создал список из словарей с данными о рейсах, вместо нормальных данных из бд, и что вы мне сделаете?
from datetime import date, datetime

flights = [
    {"flight_from": "Москва", "flight_to": "Санкт-Петербург", "airline": "Аэрофлот", 
     "time_in_flight": datetime(2025, 12, 20, 2, 0), "day_of_departure": date(2025, 12, 20), 
     "price": 4500.00, "amount_of_transfers": 0},

    {"flight_from": "Новосибирск", "flight_to": "Екатеринбург", "airline": "S7 Airlines", 
     "time_in_flight": datetime(2025, 12, 21, 3, 30), "day_of_departure": date(2025, 12, 21), 
     "price": 5300.00, "amount_of_transfers": 1},

    {"flight_from": "Казань", "flight_to": "Самара", "airline": "Utair", 
     "time_in_flight": datetime(2025, 12, 22, 1, 50), "day_of_departure": date(2025, 12, 22), 
     "price": 2900.00, "amount_of_transfers": 0},

    {"flight_from": "Краснодар", "flight_to": "Сочи", "airline": "Победа", 
     "time_in_flight": datetime(2025, 12, 23, 1, 0), "day_of_departure": date(2025, 12, 23), 
     "price": 1500.00, "amount_of_transfers": 0},

    {"flight_from": "Омск", "flight_to": "Владивосток", "airline": "Аэрофлот", 
     "time_in_flight": datetime(2025, 12, 24, 7, 45), "day_of_departure": date(2025, 12, 24), 
     "price": 9800.00, "amount_of_transfers": 1},

    {"flight_from": "Москва", "flight_to": "Париж", "airline": "Air France", 
     "time_in_flight": datetime(2025, 12, 25, 4, 10), "day_of_departure": date(2025, 12, 25), 
     "price": 18500.00, "amount_of_transfers": 0},

    {"flight_from": "Санкт-Петербург", "flight_to": "Берлин", "airline": "Lufthansa", 
     "time_in_flight": datetime(2025, 12, 26, 3, 45), "day_of_departure": date(2025, 12, 26), 
     "price": 16200.00, "amount_of_transfers": 1},

    {"flight_from": "Москва", "flight_to": "Нью-Йорк", "airline": "Aeroflot", 
     "time_in_flight": datetime(2025, 12, 27, 10, 30), "day_of_departure": date(2025, 12, 27), 
     "price": 48200.00, "amount_of_transfers": 0},

    {"flight_from": "Екатеринбург", "flight_to": "Дубай", "airline": "Emirates", 
     "time_in_flight": datetime(2025, 12, 28, 5, 50), "day_of_departure": date(2025, 12, 28), 
     "price": 32700.00, "amount_of_transfers": 0},

    {"flight_from": "Владивосток", "flight_to": "Токио", "airline": "ANA", 
     "time_in_flight": datetime(2025, 12, 29, 3, 30), "day_of_departure": date(2025, 12, 29), 
     "price": 22400.00, "amount_of_transfers": 0},

    {"flight_from": "Москва", "flight_to": "Стамбул", "airline": "Turkish Airlines", 
     "time_in_flight": datetime(2025, 12, 20, 4, 0), "day_of_departure": date(2025, 12, 20), 
     "price": 17500.00, "amount_of_transfers": 0},

    {"flight_from": "Сочи", "flight_to": "Анталья", "airline": "Pegasus Airlines", 
     "time_in_flight": datetime(2025, 12, 21, 9, 15), "day_of_departure": date(2025, 12, 21), 
     "price": 12000.00, "amount_of_transfers": 0},

    {"flight_from": "Калуга", "flight_to": "Минск", "airline": "Belavia", 
     "time_in_flight": datetime(2025, 12, 22, 6, 5), "day_of_departure": date(2025, 12, 22), 
     "price": 8000.00, "amount_of_transfers": 0},

    {"flight_from": "Москва", "flight_to": "Лондон", "airline": "British Airways", 
     "time_in_flight": datetime(2025, 12, 23, 7, 20), "day_of_departure": date(2025, 12, 23), 
     "price": 21500.00, "amount_of_transfers": 0},

    {"flight_from": "Воронеж", "flight_to": "Рим", "airline": "Alitalia", 
     "time_in_flight": datetime(2025, 12, 24, 2, 40), "day_of_departure": date(2025, 12, 24), 
     "price": 17500.00, "amount_of_transfers": 0},

    {"flight_from": "Мурманск", "flight_to": "Амстердам", "airline": "KLM", 
     "time_in_flight": datetime(2025, 12, 25, 11, 10), "day_of_departure": date(2025, 12, 25), 
     "price": 19800.00, "amount_of_transfers": 0},

    {"flight_from": "Ростов-на-Дону", "flight_to": "Прага", "airline": "Czech Airlines", 
     "time_in_flight": datetime(2025, 12, 26, 9, 50), "day_of_departure": date(2025, 12, 26), 
     "price": 12500.00, "amount_of_transfers": 0},

    {"flight_from": "Уфа", "flight_to": "Астана", "airline": "Air Astana", 
     "time_in_flight": datetime(2025, 12, 27, 4, 0), "day_of_departure": date(2025, 12, 27), 
     "price": 14800.00, "amount_of_transfers": 0},

    {"flight_from": "Калининград", "flight_to": "Мюнхен", "airline": "Lufthansa", 
     "time_in_flight": datetime(2025, 12, 28, 5, 30), "day_of_departure": date(2025, 12, 28), 
     "price": 18500.00, "amount_of_transfers": 0},

    {"flight_from": "Челябинск", "flight_to": "Хельсинки", "airline": "Finnair", 
     "time_in_flight": datetime(2025, 12, 29, 1, 50), "day_of_departure": date(2025, 12, 29), 
     "price": 15500.00, "amount_of_transfers": 0},
]
