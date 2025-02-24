from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.messages import get_messages
from django.core import mail
from django.core.cache import cache
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from apps.users.models import CustomUser
from unittest.mock import patch

class HomeViewTest(TestCase):
    def test_home_anonymous(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "LOG IN")

    def test_home_authenticated(self):
        user = CustomUser.objects.create_user(
            email='test@example.ac.uk',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            preferred_name='Johnny'
        )
        self.client.login(email='test@example.ac.uk', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertContains(response, "Logout")

    def test_login_page_contains_signup_link(self):
        response = self.client.get(reverse('log_in'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign up")


class LogInViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.ac.uk',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            preferred_name='Johnny'
        )
        self.url = reverse('log_in')

    def test_get_login_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_successful_login(self):
        response = self.client.post(self.url, {
            'email': 'test@example.ac.uk',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('home'))

    def test_invalid_login(self):
        response = self.client.post(self.url, {
            'email': 'test@example.ac.uk',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Invalid email or password.")


class LogOutViewTest(TestCase):
    def test_logout(self):
        user = CustomUser.objects.create_user(
            email='test@example.ac.uk',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            preferred_name='Johnny'
        )
        self.client.login(email='test@example.ac.uk', password='testpass123')
        response = self.client.get(reverse('log_out'))
        self.assertRedirects(response, reverse('home'))
        self.assertFalse('_auth_user_id' in self.client.session)


class PasswordViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.ac.uk',
            password='oldpassword',
            first_name='John',
            last_name='Doe',
            preferred_name='Johnny'
        )
        self.client.login(email='test@example.ac.uk', password='oldpassword')
        self.url = reverse('password')

    def test_password_change_success(self):
        response = self.client.post(self.url, {
            'password': 'oldpassword',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123'
        })
        self.assertRedirects(response, reverse('home'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123'))

    def test_password_mismatch(self):
        response = self.client.post(self.url, {
            'password': 'oldpassword',
            'new_password': 'NewPassword123',
            'password_confirmation': 'DifferentPassword'
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('Confirmation does not match password.', form.errors['password_confirmation'])


class ProfileUpdateViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.ac.uk',
            first_name='John',
            last_name='Doe',
            preferred_name='Johnny',
            password='testpass123'
        )
        self.client.login(email='test@example.ac.uk', password='testpass123')
        self.url = reverse('profile')

    def test_profile_update(self):
        response = self.client.post(self.url, {
            'email': 'updated@example.ac.uk',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'preferred_name': 'Janey'
        })
        self.assertRedirects(response, reverse('home'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Jane')
        self.assertEqual(self.user.preferred_name, 'Janey')


@override_settings(DOMAIN_NAME='testserver')
class SignUpViewTest(TestCase):
    def setUp(self):
        self.url = reverse('sign_up')
        self.valid_data = {
            'email': 'new@university.ac.uk',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'preferred_name': 'Ally',
            'new_password': 'SecurePass123',
            'password_confirmation': 'SecurePass123'
        }
        cache.clear()

    def test_get_signup_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')

    def test_successful_signup_sends_email(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Please check your email to confirm your account.")

        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Activate your account")
        self.assertEqual(mail.outbox[0].to, [self.valid_data['email']])

    def test_email_timeout(self):
        # First request
        self.client.post(self.url, self.valid_data)

        # Second immediate request
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.content.decode(), "Please wait 5 minutes before requesting another verification email.")

    def test_invalid_email_domain(self):
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'test@gmail.com'
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Only .ac.uk email addresses are allowed.', response.context['form'].errors['email'])


class ActivateAccountTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@university.ac.uk',
            'first_name': 'Test',
            'last_name': 'User',
            'preferred_name': 'Tester',
            'password': 'SecurePass123'
        }
        self.token = 'testtoken123'
        cache.clear()

    def test_successful_activation(self):
        # Store user data in cache
        cache.set(self.token, self.user_data, 3600)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user_data['email']))

        url = reverse('activate', kwargs={'uidb64': uidb64, 'token': self.token})
        response = self.client.get(url)

        # Check user was created
        self.assertTrue(CustomUser.objects.filter(email=self.user_data['email']).exists())
        user = CustomUser.objects.get(email=self.user_data['email'])
        self.assertTrue(user.is_active)

        # Check response
        self.assertRedirects(response, reverse('home'))

    def test_invalid_token(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user_data['email']))
        url = reverse('activate', kwargs={'uidb64': uidb64, 'token': 'invalidtoken'})
        response = self.client.get(url)
        self.assertEqual(response.content.decode(), "Activation link is invalid or has expired!")

    def test_mismatched_email(self):
        # Store user data in cache
        cache.set(self.token, self.user_data, 3600)
        wrong_email = 'wrong@university.ac.uk'
        uidb64 = urlsafe_base64_encode(force_bytes(wrong_email))

        url = reverse('activate', kwargs={'uidb64': uidb64, 'token': self.token})
        response = self.client.get(url)
        self.assertEqual(response.content.decode(), "Activation link is invalid!")

    def test_already_registered_email(self):
        # Create user first
        CustomUser.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            preferred_name=self.user_data['preferred_name']
        )

        # Try to activate same email
        cache.set(self.token, self.user_data, 3600)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user_data['email']))
        url = reverse('activate', kwargs={'uidb64': uidb64, 'token': self.token})
        response = self.client.get(url)
        self.assertEqual(response.content.decode(), "This email is already registered!")
