from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.societies.models import Society

class SocietyModelTest(TestCase):

    def setUp(self):
        # Create a test user with CustomUser model
        self.user = get_user_model().objects.create_user(
            email='test@example.ac.uk',
            password='password123',
            first_name='Test',
            last_name='User',
            preferred_name='Tester'
        )

        self.society = Society.objects.create(
            name="Tech Club",
            description="A society for tech enthusiasts.",
            society_type="Technology",
            status="pending",
            membership_request_required=True,
            manager=self.user
        )

    def test_society_creation(self):
        self.assertEqual(self.society.name, "Tech Club")
        self.assertEqual(self.society.status, "pending")
        self.assertEqual(self.society.manager.email, "test@example.ac.uk")  # Changed from username to email
        self.assertTrue(self.society.membership_request_required)

    def test_is_customisable(self):
        self.assertFalse(self.society.is_customisable())  # the default is "pending"

        self.society.status = "approved"
        self.society.save()
        self.assertTrue(self.society.is_customisable())

    def test_default_values(self):
        new_society = Society.objects.create(
            name="Music Club",
            description="A society for music lovers.",
            society_type="Cultural",
            manager=self.user
        )
        self.assertEqual(new_society.status, "pending")
        self.assertFalse(new_society.membership_request_required)

    def test_unique_society_name(self):
        with self.assertRaises(Exception):
            Society.objects.create(
                name="Tech Club",  # same name as before
                description="Another tech club",
                society_type="Technology",
                manager=self.user
            )
