from django.urls import path
from . import views

urlpatterns = [
    path('', views.FlightListView.as_view(), name='list_tickets'),
    path('tickets/', views.FlightListView.as_view(), name='list_tickets'),
    path('tickets/<slug:slug>/', views.FlightDetailView.as_view(), name='flight_detail'),
    path('tickets/<slug:slug>/purchase/', views.BuyTicketView.as_view(), name='ticket_purchase'),
    path('ticket_ordered/', views.TicketOrderedView.as_view(), name='ticket_ordered'),
    path('ticket_not_ordered/', views.TicketNotOrderedView.as_view(), name='ticket_not_ordered'),
    path('cancel_ticket/<int:ticket_id>/', views.CancelTicketView.as_view(), name='cancel_ticket'),
]
