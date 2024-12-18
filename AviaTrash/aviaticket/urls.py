from django.urls import path
from . import views

urlpatterns = [
    path('', views.FlightListView.as_view(), name='list_tickets'),
]
