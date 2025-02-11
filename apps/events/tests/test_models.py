from django.test import TestCase
from django.utils import timezone
from apps.events.models import Event, EventRegistration
from django.contrib.auth import get_user_model
from apps.societies.models import Society

class EventModelTest(TestCase):
    def setUp(self):
        self.test_society = Society.objects.create(
            name="Chess Club",
            description="A club for chess lovers",
            society_type="sports",
            status="approved"
        )

        self.event = Event.objects.create(
            name="Chess Tournament",
            location="Manchester",
            date=timezone.now() + timezone.timedelta(days=7),
            event_type="sports",
            keyword="chess",
            is_free=True,
            members_only=False,
            capacity=100
        )

    def test_event_creation(self):
        """Test if an event is created with the correct values."""
        self.assertEqual(self.event.name, "Chess Tournament")
        self.assertEqual(self.event.event_type, "sports")
        self.assertTrue(self.event.is_free)
        self.assertFalse(self.event.members_only)
        self.assertEqual(self.event.capacity, 100)

    def test_str_representation(self):
        """Test the __str__ method of the Event model."""
        expected_str = f"{self.event.name} - {self.event.event_type}"
        self.assertEqual(str(self.event), expected_str)


class EventRegistrationModelTest(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = get_user_model().objects.create_user(
            email="john.doe@university.ac.uk",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="testpassword123"
        )

        # Create an event
        self.event = Event.objects.create(
            name="Art Workshop",
            location="Online",
            date=timezone.now() + timezone.timedelta(days=3),
            event_type="arts",
            keyword="painting",
            is_free=False,
            members_only=True,
            capacity=50
        )

        # Create an event registration
        self.registration = EventRegistration.objects.create(
            event=self.event,
            user=self.user,
            status='accepted'
        )

    def test_event_registration_creation(self):
        """Ensure an event registration is created with the correct values."""
        self.assertEqual(self.registration.event, self.event)
        self.assertEqual(self.registration.user, self.user)
        self.assertEqual(self.registration.status, 'accepted')
        self.assertIsNotNone(self.registration.registration_date)

    def test_default_status(self):
        """Test that if no status is given, the default is 'waitlisted'."""
        new_registration = EventRegistration.objects.create(
            event=self.event,
            user=self.user
        )
        self.assertEqual(new_registration.status, 'waitlisted')

    def test_str_representation(self):
        """Test the __str__ method of the EventRegistration model."""
        expected_str = f"{self.registration.user} - {self.registration.event} - accepted"
        self.assertEqual(str(self.registration), expected_str)
