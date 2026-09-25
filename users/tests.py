from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import User

PASSWORD = "Secret-pass-123"


class RegistrationTests(TestCase):
    url = reverse("users:register")

    def payload(self, **overrides):
        data = {
            "username": "ivan",
            "email": "Ivan@Example.com",
            "first_name": "Иван",
            "last_name": "Иванов",
            "password1": PASSWORD,
            "password2": PASSWORD,
        }
        return data | overrides

    def test_register_logs_in_and_redirects_to_flights(self):
        response = self.client.post(self.url, self.payload())

        self.assertRedirects(response, reverse("aviaticket:flight_list"))
        user = User.objects.get()
        self.assertEqual(user.email, "ivan@example.com")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_email_must_be_unique_case_insensitive(self):
        User.objects.create_user("petr", "ivan@example.com", PASSWORD)
        response = self.client.post(self.url, self.payload(email="IVAN@example.com"))
        self.assertFormError(
            response.context["form"], "email", "Пользователь с таким e-mail уже зарегистрирован."
        )

    def test_names_are_required(self):
        response = self.client.post(self.url, self.payload(first_name=""))
        self.assertTrue(response.context["form"].has_error("first_name"))

    def test_authenticated_user_is_redirected(self):
        self.client.force_login(User.objects.create_user("petr", "petr@example.com", PASSWORD))
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("aviaticket:flight_list"))


class LoginTests(TestCase):
    def setUp(self):
        User.objects.create_user("ivan", "ivan@example.com", PASSWORD)

    def test_login_respects_next(self):
        target = reverse("aviaticket:ticket_list")
        response = self.client.post(
            f"{reverse('users:login')}?next={target}",
            {"username": "ivan", "password": PASSWORD, "next": target},
        )
        self.assertRedirects(response, target)

    def test_protected_page_redirects_to_our_login(self):
        response = self.client.get(reverse("users:profile"))
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('users:profile')}")

    def test_logout_is_post(self):
        self.client.login(username="ivan", password=PASSWORD)
        response = self.client.post(reverse("users:logout"))
        self.assertRedirects(response, reverse("aviaticket:flight_list"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ivan", "ivan@example.com", PASSWORD)
        self.client.force_login(self.user)
        self.url = reverse("users:profile")

    def test_update_profile(self):
        response = self.client.post(
            self.url,
            {
                "first_name": "Иван",
                "last_name": "Иванов",
                "email": "ivan@example.com",
                "phone": "+7 999 123-45-67",
                "birth_date": "2000-01-31",
            },
            follow=True,
        )

        self.assertContains(response, "Данные профиля сохранены.")
        self.user.refresh_from_db()
        self.assertEqual(self.user.display_name, "Иван Иванов")
        self.assertEqual(self.user.birth_date.isoformat(), "2000-01-31")

    def test_birth_date_in_future_is_rejected(self):
        tomorrow = timezone.localdate() + timedelta(days=1)
        response = self.client.post(
            self.url, {"email": "ivan@example.com", "birth_date": tomorrow.isoformat()}
        )
        self.assertTrue(response.context["form"].has_error("birth_date"))

    def test_invalid_form_does_not_leak_into_header(self):
        response = self.client.post(self.url, {"first_name": "Хакер", "email": "broken"})
        self.assertNotContains(response, "Хакер</span>")

    def test_password_change_redirects_to_profile(self):
        response = self.client.post(
            reverse("users:password_change"),
            {
                "old_password": PASSWORD,
                "new_password1": "Another-pass-456",
                "new_password2": "Another-pass-456",
            },
        )
        self.assertRedirects(response, self.url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Another-pass-456"))
