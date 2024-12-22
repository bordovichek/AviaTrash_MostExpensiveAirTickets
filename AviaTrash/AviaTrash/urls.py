from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tickets/', include('aviaticket.urls')),  # Маршруты для приложения ticket
    path('personal/', include('users.urls')),  # Маршруты для приложения users
    path('', lambda request: redirect('tickets/', permanent=True)),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)