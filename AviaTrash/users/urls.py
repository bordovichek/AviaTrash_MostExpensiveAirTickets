from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import RegisterUserView, LoginUser, ProfileUser, CustomPasswordChangeView

app_name = 'personal'

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='personal:login'), name='logout'),
    path('profile/', ProfileUser.as_view(), name='profile'),
    path('profile/password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
]
