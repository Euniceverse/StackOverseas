from django.urls import resolve, reverse
from django.test import SimpleTestCase
from apps.users import views

class UsersUrlsTest(SimpleTestCase):
    def test_account_url_resolves(self):
        url = reverse('accountpage')
        self.assertEqual(resolve(url).func, views.accountpage)

    def test_login_url_resolves(self):
        url = reverse('log_in')
        self.assertEqual(resolve(url).func.view_class, views.LogInView)

    def test_logout_url_resolves(self):
        url = reverse('log_out')
        self.assertEqual(resolve(url).func, views.log_out)

    def test_password_url_resolves(self):
        url = reverse('password')
        self.assertEqual(resolve(url).func.view_class, views.PasswordView)

    def test_profile_url_resolves(self):
        url = reverse('profile')
        self.assertEqual(resolve(url).func.view_class, views.ProfileUpdateView)

    def test_signup_url_resolves(self):
        url = reverse('sign_up')
        self.assertEqual(resolve(url).func.view_class, views.SignUpView)

    def test_activate_url_resolves(self):
        url = reverse('activate', kwargs={'uidb64': 'dummy', 'token': 'dummy'})
        self.assertEqual(resolve(url).func, views.activate)

    def test_forgot_password_url_resolves(self):
        url = reverse('forgot_password')
        self.assertEqual(resolve(url).func.view_class, views.ForgotPasswordView)

    def test_reset_password_url_resolves(self):
        url = reverse('reset_password', kwargs={'token': 'dummy'})
        self.assertEqual(resolve(url).func.view_class, views.ResetPasswordView)

    def test_annual_verify_url_resolves(self):
        url = reverse('annual_verify', kwargs={'uidb64': 'dummy', 'token': 'dummy'})
        self.assertEqual(resolve(url).func, views.annual_verify)