from datetime import datetime
from django.core.paginator import Paginator
from django.shortcuts import render
from .flight_data import flights

def ticket_list(request):
    sorted_flights = sorted(flights, key=lambda x: x['day_of_departure'])
    paginator = Paginator(sorted_flights, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'aviaticket/ticket_list.html', {'page_obj': page_obj})

# да, да я знаю, плохо брать данные из словарика, но чуть позже добавлю записи в бд и буду брать их от туда