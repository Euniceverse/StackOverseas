from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.users.models import CustomUser

User = get_user_model()

class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # ensure user is active
        self.user = CustomUser.objects.create_user(
            email="testuser@uni.ac.uk",
            first_name="Test",
            last_name="User",
            preferred_name="Tester",
            password="testpassword"
        )
        self.user.is_active = True
        self.user.save()

    def test_accountpage_requires_login(self):
        response = self.client.get(reverse("accountpage"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("users/login", response.url)

    def test_accountpage_context(self):
        self.client.login(email="testuser@uni.ac.uk", password="testpassword")
        response = self.client.get(reverse("accountpage"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("societies", response.context)
        self.assertIn("managed_societies", response.context)
        self.assertIn("memberships", response.context)

    def test_login_view_get(self):
        response = self.client.get(reverse("log_in"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "log_in.html")

    def test_login_view_post_valid(self):
        response = self.client.post(reverse("log_in"), {
            "email": "testuser@uni.ac.uk",
            "password": "testpassword"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

    def test_login_view_post_invalid(self):
        response = self.client.post(reverse("log_in"), {
            "email": "testuser@uni.ac.uk",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "log_in.html")
        self.assertContains(response, "Invalid email or password.")

    def test_log_out_view(self):
        self.client.login(email="testuser@uni.ac.uk", password="testpassword")
        response = self.client.get(reverse("log_out"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))
        response = self.client.get(reverse("accountpage"))
        self.assertEqual(response.status_code, 302)

    def test_password_view_sends_email(self):
        self.client.login(email="testuser@uni.ac.uk", password="testpassword")
        response = self.client.get(reverse("password"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "password_confirmation.html")

    def test_forgot_password_get(self):
        response = self.client.get(reverse("forgot_password"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "forgot_password.html")

    def test_forgot_password_post_valid(self):
        original_send = EmailMessage.send
        EmailMessage.send = lambda self: 1
        response = self.client.post(reverse("forgot_password"), {"email": "testuser@uni.ac.uk"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "If an account exists")
        EmailMessage.send = original_send

    def test_reset_password_invalid_token(self):
        response = self.client.get(reverse("reset_password", kwargs={"token": "invalid"}))
        self.assertEqual(response.status_code, 302)
        self.assertIn("users/login", response.url)

    def test_profile_update_view_get(self):
        self.client.login(email="testuser@uni.ac.uk", password="testpassword")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")

    def test_sign_up_view_get(self):
        response = self.client.get(reverse("sign_up"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "sign_up.html")

    def test_sign_up_view_post(self):
        email = "newuser@uni.ac.uk"
        cache_key = f"email_timeout_{email}"
        cache.delete(cache_key)
        post_data = {
            "email": email,
            "first_name": "New",
            "last_name": "User",
            "preferred_name": "Newbie",
            "new_password": "Password123",
            "password_confirmation": "Password123",
            "terms_accepted": "on"
        }
        response = self.client.post(reverse("sign_up"), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please check your email to confirm your account.")

    def test_activate_view(self): # simulate activation
        token = "activationtoken123"
        user_data = {
            "email": "activate@uni.ac.uk",
            "first_name": "Activate",
            "last_name": "User",
            "preferred_name": "Activator",
            "password": "activatepass"
        }
        cache.set(token, user_data, 3600)
        uidb64 = urlsafe_base64_encode(force_bytes(user_data["email"]))
        response = self.client.get(reverse("activate", kwargs={"uidb64": uidb64, "token": token}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CustomUser.objects.filter(email="activate@uni.ac.uk").exists())

    def test_annual_verify_view(self):
        token = "verifytoken123"
        email = "testuser@uni.ac.uk"
        cache_key = f"annual_verify_{token}"
        cache.set(cache_key, email, 3600)
        uidb64 = urlsafe_base64_encode(force_bytes(email))
        response = self.client.get(reverse("annual_verify", kwargs={"uidb64": uidb64, "token": token}))
        self.assertEqual(response.status_code, 302)
        user = CustomUser.objects.get(email=email)
        self.assertIsNotNone(user.annual_verification_date)