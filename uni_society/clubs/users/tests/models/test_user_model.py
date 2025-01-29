'''
we want to ensure the following with testing
users created correctly (valid email)
email validation tests
superusers created correctly
preferred names change once a year with verification
'''

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from users.models import CustomUser

class CustomUserModelTest(TestCase):

    def setUp(self):
        """Setup default users for testing."""
        self.user = CustomUser.objects.create_user(
            email="student@university.ac.uk",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="testpassword123"
        )
        self.admin = CustomUser.objects.create_superuser(
            email="admin@university.ac.uk",
            first_name="Admin",
            last_name="User",
            preferred_name="Admin",
            password="adminpassword"
        )

    def test_user_creation(self):
        """Test if a user is created properly."""
        self.assertEqual(self.user.email, "student@university.ac.uk")
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.preferred_name, "Johnny")
        self.assertFalse(self.user.is_staff)  # Regular users are not staff
        self.assertFalse(self.user.is_superuser)  # Regular users are not superusers

    def test_superuser_creation(self):
        """Test if a superuser is created properly."""
        self.assertTrue(self.admin.is_staff)
        self.assertTrue(self.admin.is_superuser)

    def test_valid_ac_uk_email(self):
        """Test that only .ac.uk emails are allowed."""
        valid_user = CustomUser.objects.create_user(
            email="student2@college.ac.uk",
            first_name="Alice",
            last_name="Smith",
            preferred_name="Ali",
            password="testpassword"
        )
        self.assertEqual(valid_user.email, "student2@college.ac.uk")

    def test_invalid_email(self):
        """Test that emails not ending in .ac.uk raise a ValidationError."""
        with self.assertRaises(ValidationError):
            invalid_user = CustomUser(
                email="testuser@gmail.com", 
                first_name="John",
                last_name="Doe",
                preferred_name="Johnny"
            )
            invalid_user.full_clean()  # Runs model validation before saving

    def test_edge_case_email(self):
        """Test that an email that almost matches .ac.uk (but isn't) is rejected."""
        with self.assertRaises(ValidationError):
            invalid_user = CustomUser(
                email="student@university.ac.com",  # Incorrect domain
                first_name="Jane",
                last_name="Doe",
                preferred_name="Janey"
            )
            invalid_user.full_clean()

    def test_preferred_name_change_requires_email_verification(self):
        """Test that users must verify their email before changing their preferred name."""
        self.user.last_verified_date = timezone.now() - timedelta(days=365)  # Make user eligible
        self.user.save()
        
        self.assertTrue(self.user.can_change_preferred_name())

        # Attempt to update preferred name (should require verification)
        self.assertFalse(self.user.update_preferred_name("NewJohnny"))

        # Email verification must be confirmed before change
        self.user.confirm_preferred_name_change("NewJohnny")
        self.assertEqual(self.user.preferred_name, "NewJohnny")
        self.assertFalse(self.user.can_change_preferred_name())  # Now must wait another year

    def test_cannot_change_preferred_name_twice_in_one_year(self):
        """Test that users cannot change their preferred name more than once a year."""
        self.user.last_verified_date = timezone.now() - timedelta(days=365)  # Make user eligible
        self.user.confirm_preferred_name_change("NewJohnny")

        # Try to change again immediately
        with self.assertRaises(ValidationError):
            self.user.update_preferred_name("AnotherName")

    def test_email_verification_updates_last_verified_date(self):
        """Test that verifying email updates last_verified_date."""
        old_date = timezone.now() - timedelta(days=366)
        self.user.last_verified_date = old_date
        self.user.save()

        self.user.verify_email()  # Simulate email verification

        self.assertNotEqual(self.user.last_verified_date, old_date)
        self.assertGreater(self.user.last_verified_date, old_date)

    def test_cannot_change_preferred_name_without_waiting_a_year(self):
        """Test that users cannot change their preferred name again within a year."""
        self.user.last_verified_date = timezone.now()  # Just verified
        self.user.save()

        self.assertFalse(self.user.can_change_preferred_name())

        with self.assertRaises(ValidationError):
            self.user.update_preferred_name("NewNameTooSoon")

    def test_can_change_preferred_name_after_one_year(self):
        """Test that users can change their preferred name after a year has passed."""
        self.user.last_verified_date = timezone.now() - timedelta(days=366)
        self.user.save()

        self.assertTrue(self.user.can_change_preferred_name())
        self.user.confirm_preferred_name_change("NewJohnny")
        self.assertEqual(self.user.preferred_name, "NewJohnny")
