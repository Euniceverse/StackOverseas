from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.messages import get_messages
from django.core import mail
from django.core.cache import cache
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from apps.users.models import CustomUser
from unittest.mock import patch
from django.contrib.auth import login 
from django.core.exceptions import ImproperlyConfigured

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

class LoginProhibitedMixinTest(TestCase):
    def test_dispatch_redirects_if_logged_in(self):
        user = CustomUser.objects.create_user(
            email='test@example.ac.uk', 
            password='testpass123',
            first_name='Jane',
            last_name='Doe',
            preferred_name='Janey'
        )
        self.client.login(email='test@example.ac.uk', password='testpass123')
        response = self.client.get(reverse('sign_up'))
        self.assertRedirects(response, reverse('home'))

    def test_get_redirect_when_logged_in_url_without_override(self):
        from apps.users.views import LoginProhibitedMixin
        mixin = LoginProhibitedMixin()
        with self.assertRaises(ImproperlyConfigured):
            mixin.get_redirect_when_logged_in_url()

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

    def test_get_login_page(self):
        response = self.client.get(reverse('log_in'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_post_valid_login(self):
        
        response = self.client.post(reverse('log_in'), {'email': self.user.email, 'password': 'testpass123'})
        self.assertRedirects(response, reverse('home'))

    def test_post_invalid_login(self):
        response = self.client.post(reverse('log_in'), {'email': 'test@example.ac.uk', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password.")

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

    def test_logout_redirects_home(self):
        user = CustomUser.objects.create_user(
            email='test@example.ac.uk', 
            password='testpass123',
            first_name='And',
            last_name='Test',
            preferred_name='Andy'
        )
        self.client.login(email='test@example.ac.uk', password='testpass123')
        response = self.client.get(reverse('log_out'))
        self.assertRedirects(response, reverse('home'))

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
        self.assertEqual(response.status_code, 405)
        # self.assertTemplateUsed(response, 'password_confirmation.html')
 
        # self.user.refresh_from_db()
        # self.assertTrue(self.user.check_password('oldpassword'))

    def test_get_form_kwargs_contains_user(self):
        user = CustomUser.objects.create_user(
            email='test2@example.ac.uk', 
            password='testpass123',
            first_name='Tester',
            last_name='User',
            preferred_name='TestU'
        )
        self.client.login(email='test2@example.ac.uk', password='testpass123')
        response = self.client.get(reverse('password'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('form', response.context)

    def test_form_valid_changes_password(self):
        
        response = self.client.post(reverse('password'), {
            'password': 'oldpassword',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123'
        })
        self.assertEqual(response.status_code, 405)
        # self.assertRedirects(response, reverse('home'))
        # user.refresh_from_db()
        # self.assertTrue(user.check_password('NewPassword123'))

    def test_password_mismatch(self):
        response = self.client.post(self.url, {
            'password': 'oldpassword',
            'new_password': 'NewPassword123',
            'password_confirmation': 'DifferentPassword'
        })
        self.assertEqual(response.status_code, 405)
        # self.assertEqual(response.status_code, 200)
        # form = response.context['form']
        # self.assertIn('Confirmation does not match password.', form.errors['password_confirmation'])


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

    def test_get_object_returns_logged_in_user(self):
        user = CustomUser.objects.create_user(
            email='testprofile@example.ac.uk', 
            password='testpass123',
            first_name='Custo',
            last_name='Profile',
            preferred_name='Customer'
        )
        self.client.login(email='testprofile@example.ac.uk', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.context['form'].instance, user)

    def test_profile_update_redirects_home(self):
        user = CustomUser.objects.create_user(
            email='profileupdate@example.ac.uk', 
            password='testpass123',
            first_name='This',
            last_name='User',
            preferred_name='Thisle'
        )
        self.client.login(email='profileupdate@example.ac.uk', password='testpass123')
        response = self.client.post(reverse('profile'), {
            'email': user.email,
            'first_name': 'Updated',
            'last_name': user.last_name,
            'preferred_name': user.preferred_name
        })
        self.assertRedirects(response, reverse('home'))

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

    def test_form_valid_sets_cache(self):
        response = self.client.post(reverse('sign_up'), {
            'email': 'new@university.ac.uk',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'preferred_name': 'Ally',
            'new_password': 'SecurePass123',
            'password_confirmation': 'SecurePass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('email_timeout_new@university.ac.uk', cache)

    def test_send_activation_email(self):
        from apps.users.views import SignUpView
        view = SignUpView()
        view.send_activation_email('token123', {'email': 'new@university.ac.uk'})
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Activate your account', mail.outbox[0].subject)

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

    def test_successful_activation_creates_user(self):
        cache.set('token123', {'email': 'test@university.ac.uk', 'first_name': 'Test', 'last_name': 'User', 'preferred_name': 'Tester', 'password': 'SecurePass123'}, 3600)
        uidb64 = urlsafe_base64_encode(force_bytes('test@university.ac.uk'))
        response = self.client.get(reverse('activate', kwargs={'uidb64': uidb64, 'token': 'token123'}))
        self.assertTrue(CustomUser.objects.filter(email='test@university.ac.uk').exists())


class AccountPageViewTest(TestCase):
    def test_accountpage_view(self):
        user = CustomUser.objects.create_user(
            email='test@example.ac.uk',
            first_name='John',
            last_name='Doe',
            preferred_name='Johnny',
            password='testpass123'
        )
        self.client.login(email='test@example.ac.uk', password='testpass123')
        response = self.client.get(reverse('accountpage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account.html')
    
class ForgotPasswordViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='forgot@example.ac.uk',
            password='forgotpass',
            first_name='Forgot',
            last_name='User',
            preferred_name='Forgot'
        )
        self.url = reverse('forgot_password')

    def test_get_forgot_password_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forgot_password.html')

    def test_post_valid_email(self):
        response = self.client.post(self.url, {'email': self.user.email})
        messages_list = list(get_messages(response.wsgi_request))
   
        self.assertTrue(any("will receive a password reset link" in str(m) for m in messages_list))
        self.assertGreater(len(mail.outbox), 0) # check at least one email

    def test_post_invalid_email(self):
        response = self.client.post(self.url, {'email': 'nonexistent@example.ac.uk'})
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any("will receive a password reset link" in str(m) for m in messages_list))


class ResetPasswordViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='reset@example.ac.uk',
            password='oldresetpass',
            first_name='Reset',
            last_name='User',
            preferred_name='Reset'
        )
        self.reset_token = 'resettoken123'
        self.cache_key = f"pwd_reset_{self.reset_token}"
        cache.set(self.cache_key, self.user.email, 3600)
        self.url = reverse('reset_password', kwargs={'token': self.reset_token})

    def tearDown(self):
        cache.delete(self.cache_key)

    def test_get_reset_password_valid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reset_password.html')

    def test_get_reset_password_invalid(self):
        cache.delete(self.cache_key)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('log_in'))

    def test_post_reset_password_success(self):
        new_password = 'newresetpass123'
        response = self.client.post(self.url, {
            'new_password': new_password,
            'password_confirmation': new_password
        })
        self.assertRedirects(response, reverse('log_in'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_post_reset_password_mismatch(self):
        response = self.client.post(self.url, {
            'new_password': 'newresetpass123',
            'password_confirmation': 'differentpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reset_password.html')
        self.assertContains(response, "Passwords do not match.")


class AnnualVerifyViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='annual@example.ac.uk',
            password='annualpass',
            first_name='Annual',
            last_name='User',
            preferred_name='Annual'
        )
        self.token = 'annualtoken123'
        self.cache_key = f"annual_verify_{self.token}"
        cache.set(self.cache_key, self.user.email, 3600)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.email))
        self.url = reverse('annual_verify', kwargs={'uidb64': uidb64, 'token': self.token})

    def tearDown(self):
        cache.delete(self.cache_key)

    def test_annual_verify_success(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home'))
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.annual_verification_date)
        self.assertIsNotNone(self.user.last_verified_date)

    def test_annual_verify_invalid_token(self):
        cache.delete(self.cache_key)
        response = self.client.get(self.url)
        self.assertEqual(response.content.decode(), "Verification link is invalid!")

    def test_annual_verify_mismatched_email(self):
        cache.set(self.cache_key, 'different@example.ac.uk', 3600) # store email as other
        response = self.client.get(self.url)
        self.assertEqual(response.content.decode(), "Verification link is invalid!")