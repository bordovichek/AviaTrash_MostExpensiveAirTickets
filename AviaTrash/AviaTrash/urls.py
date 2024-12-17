from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tickets/', include('aviaticket.urls')),  # Маршруты для приложения ticket
    #path('personal/', include('users.urls')),  # Маршруты для приложения users
]
