from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from .models import CustomUser

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


class SignUpViewTest(TestCase):
    def setUp(self):
        self.url = reverse('sign_up')

    def test_signup_success(self):
        response = self.client.post(self.url, {
            'email': 'new@university.ac.uk',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'preferred_name': 'Ally',
            'new_password': 'SecurePass123',
            'password_confirmation': 'SecurePass123'
        })
        self.assertRedirects(response, reverse('home'))
        new_user = CustomUser.objects.get(email='new@university.ac.uk')
        self.assertEqual(new_user.first_name, 'Alice')
        self.assertEqual(new_user.preferred_name, 'Ally')
        self.assertTrue(new_user.check_password('SecurePass123'))

    def test_invalid_email_domain(self):
        response = self.client.post(self.url, {
            'email': 'invalid@gmail.com',
            'first_name': 'Bob',
            'last_name': 'Jones',
            'preferred_name': 'Bobby',
            'new_password': 'SecurePass123',
            'password_confirmation': 'SecurePass123'
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('Only .ac.uk email addresses are allowed.', form.errors['email'])
