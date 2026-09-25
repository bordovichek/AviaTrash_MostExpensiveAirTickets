from django.urls import path

from . import views

app_name = "aviaticket"

urlpatterns = [
    path("", views.FlightListView.as_view(), name="flight_list"),
    path("flights/<slug:slug>/", views.FlightDetailView.as_view(), name="flight_detail"),
    path("flights/<slug:slug>/buy/", views.BuyTicketView.as_view(), name="buy_ticket"),
    path("tickets/", views.TicketListView.as_view(), name="ticket_list"),
    path("tickets/<str:pnr>/", views.TicketDetailView.as_view(), name="ticket_detail"),
    path("tickets/<str:pnr>/cancel/", views.CancelTicketView.as_view(), name="cancel_ticket"),
]
