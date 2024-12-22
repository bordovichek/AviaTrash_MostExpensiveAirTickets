import os
from aviaticket.models import CityWithPhoto
from django.core.files import File

photo_folder = r'C:\Users\slava\PycharmProjects\aviatrash\AviaTrash\aviaticket\city_media\photos'
cities_with_photos = [
{"city_name": "Санкт-Петербург", "photo": "saint_petersburg.jpg"},
{"city_name": "Екатеринбург", "photo": "ekaterenburg.jpg"},
{"city_name": "Самара", "photo": "samara.jpg"},
{"city_name": "Сочи", "photo": "sochi.jpg"},
{"city_name": "Владивосток", "photo": "vladivostok.jpg"},
{"city_name": "Париж", "photo": "paris.jpg"},
{"city_name": "Берлин", "photo": "berlin.jpg"},
{"city_name": "Нью-Йорк", "photo": "new_york.jpg"},
{"city_name": "Дубай", "photo": "dubai.jpg"},
{"city_name": "Токио", "photo": "tokio.jpg"},
{"city_name": "Стамбул", "photo": "stambul.jpg"},
{"city_name": "Анталия", "photo": "antalia.jpg"},
{"city_name": "Минск", "photo": "minsk.jpg"},
{"city_name": "Лондон", "photo": "london.jpg"},
{"city_name": "Рим", "photo": "rome.jpg"},
{"city_name": "Амстердам", "photo": "amsterdam.jpg"},
{"city_name": "Прага", "photo": "praga.jpg"},
{"city_name": "Астана", "photo": "astana.jpg"},
{"city_name": "Мюнхен", "photo": "munhen.jpg"},
{"city_name": "Хельсинки", "photo": "helsinki.jpg"},
]

for city_data in cities_with_photos:
    city = CityWithPhoto(city_name=city_data["city_name"])
    if city_data["photo"]:
        photo_path = os.path.join(photo_folder, city_data["photo"])
        if os.path.exists(photo_path):
            with open(photo_path, "rb") as photo_file:
                city.photo.save(city_data["photo"], File(photo_file))
                print(f"Фото для города {city.city_name} добавлено.")
        else:
            print(f"Файл {photo_path} для города {city.city_name} не найден. Фото не добавлено.")
    else:
        print(f"Фото для города {city.city_name} отсутствует. Пропускаем.")

    city.save()
    print(f"Город {city.city_name} сохранен.")
