from django.test import TestCase
from apps.users.models import CustomUser
from apps.users.forms import (
    UserForm,
    LogInForm,
    NewPasswordMixin,
    PasswordForm,
    SignUpForm
)

class UserFormTest(TestCase):
    def test_form_has_correct_fields(self):
        form = UserForm()
        self.assertIn('email', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('preferred_name', form.fields)

    def test_valid_form_data(self):
        data = {
            'email': 'test@example.ac.uk',
            'first_name': 'John',
            'last_name': 'Doe',
            'preferred_name': 'Johnny'
        }
        form = UserForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_saves_correctly(self):
        data = {
            'email': 'test@example.ac.uk',
            'first_name': 'John',
            'last_name': 'Doe',
            'preferred_name': 'Johnny'
        }
        form = UserForm(data=data)
        user = form.save(commit=False)
        user.save()
        self.assertEqual(user.email, 'test@example.ac.uk')


class LogInFormTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.ac.uk',
            password='ValidPassword123',
            first_name='John',
            last_name='Doe',
            preferred_name='Johnny'
        )

    def test_valid_credentials(self):
        form = LogInForm(data={
            'email': 'test@example.ac.uk',
            'password': 'ValidPassword123'
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    def test_invalid_credentials(self):
        form = LogInForm(data={
            'email': 'test@example.ac.uk',
            'password': 'WrongPassword'
        })
        self.assertFalse(form.is_valid())
        self.assertIsNone(form.get_user())

    def test_invalid_form_data(self):
        form = LogInForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password', form.errors)


class NewPasswordMixinTest(TestCase):
    def setUp(self):
        class TestForm(NewPasswordMixin):
            def clean(self):
                return super().clean()
        self.form_class = TestForm

    def test_password_validation(self):
        # Test valid password
        form = self.form_class(data={
            'new_password': 'ValidPassword123',
            'password_confirmation': 'ValidPassword123'
        })
        self.assertTrue(form.is_valid())

        # Test password without uppercase
        form = self.form_class(data={
            'new_password': 'lowercase123',
            'password_confirmation': 'lowercase123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)

        # Test password without numbers
        form = self.form_class(data={
            'new_password': 'NoNumbersHere',
            'password_confirmation': 'NoNumbersHere'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)

        # Test password too short
        form = self.form_class(data={
            'new_password': 'Short1',
            'password_confirmation': 'Short1'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)

        # Test mismatched passwords
        form = self.form_class(data={
            'new_password': 'ValidPassword123',
            'password_confirmation': 'DifferentPassword123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password_confirmation', form.errors)


class PasswordFormTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.ac.uk',
            password='OldPassword123',
            first_name='John',
            last_name='Doe',
            preferred_name='Johnny'
        )

    def test_valid_password_change(self):
        form = PasswordForm(user=self.user, data={
            'password': 'OldPassword123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123'
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(self.user.check_password('NewPassword123'))

    def test_invalid_current_password(self):
        form = PasswordForm(user=self.user, data={
            'password': 'WrongPassword',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_password_regex_validation(self):
        form = PasswordForm(user=self.user, data={
            'password': 'OldPassword123',
            'new_password': 'weakpassword',
            'password_confirmation': 'weakpassword'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)


class SignUpFormTest(TestCase):
    def test_email_validation(self):
        # Valid .ac.uk email
        form = SignUpForm(data={
            'email': 'valid@university.ac.uk',
            'first_name': 'John',
            'last_name': 'Doe',
            'preferred_name': 'Johnny',
            'new_password': 'ValidPassword123',
            'password_confirmation': 'ValidPassword123'
        })
        self.assertTrue(form.is_valid())

        # Invalid email domain
        form = SignUpForm(data={
            'email': 'invalid@gmail.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'preferred_name': 'Johnny',
            'new_password': 'ValidPassword123',
            'password_confirmation': 'ValidPassword123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_user_creation(self):
        data = {
            'email': 'newuser@university.ac.uk',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'preferred_name': 'Ally',
            'new_password': 'SecurePassword123',
            'password_confirmation': 'SecurePassword123'
        }
        form = SignUpForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, 'newuser@university.ac.uk')
        self.assertTrue(user.check_password('SecurePassword123'))

    def test_password_mismatch(self):
        form = SignUpForm(data={
            'email': 'test@example.ac.uk',
            'first_name': 'John',
            'last_name': 'Doe',
            'preferred_name': 'Johnny',
            'new_password': 'Password123',
            'password_confirmation': 'DifferentPassword'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password_confirmation', form.errors)

    def test_duplicate_email(self):
        # Create a user first
        CustomUser.objects.create_user(
            email='existing@university.ac.uk',
            password='ValidPassword123',
            first_name='John',
            last_name='Doe',
            preferred_name='Johnny'
        )

        # Try to create another user with the same email
        form = SignUpForm(data={
            'email': 'existing@university.ac.uk',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'preferred_name': 'Jane',
            'new_password': 'ValidPassword123',
            'password_confirmation': 'ValidPassword123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('This email is already registered', str(form.errors['email']))

    def test_non_academic_email(self):
        # Test various non-academic email formats
        invalid_emails = [
            'test@gmail.com',
            'test@yahoo.com',
            'test@university.com',
            'test@university.co.uk',
        ]

        for email in invalid_emails:
            form = SignUpForm(data={
                'email': email,
                'first_name': 'John',
                'last_name': 'Doe',
                'preferred_name': 'Johnny',
                'new_password': 'ValidPassword123',
                'password_confirmation': 'ValidPassword123'
            })
            self.assertFalse(form.is_valid())
            self.assertIn('email', form.errors)

        # Test malformed email addresses separately
        malformed_emails = [
            'test@.ac.uk',
            '@university.ac.uk',
        ]

        for email in malformed_emails:
            form = SignUpForm(data={
                'email': email,
                'first_name': 'John',
                'last_name': 'Doe',
                'preferred_name': 'Johnny',
                'new_password': 'ValidPassword123',
                'password_confirmation': 'ValidPassword123'
            })
            self.assertFalse(form.is_valid())
            self.assertIn('email', form.errors)

    def test_save_sets_is_active_false(self):
        form = SignUpForm(data={
            'email': 'newuser@university.ac.uk',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'preferred_name': 'Ally',
            'new_password': 'SecurePassword123',
            'password_confirmation': 'SecurePassword123'
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertFalse(user.is_active)
