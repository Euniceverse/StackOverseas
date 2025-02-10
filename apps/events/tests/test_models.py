from django.test import TestCase
from django.utils import timezone
from apps.events.models import Event, EventRegistration
from django.contrib.auth import get_user_model
from apps.societies.models import Society
from django.core.exceptions import ValidationError
from decimal import Decimal

class EventModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@university.ac.uk",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="testpass123"
        )

        self.test_society = Society.objects.create(
            name="Chess Club",
            description="A club for chess lovers",
            society_type="sports",
            status="approved",
            manager=self.user
        )

        current_date = timezone.now().date() + timezone.timedelta(days=7)
        current_time = timezone.now().time()

        self.event = Event.objects.create(
            name="Chess Tournament",
            description="Annual chess tournament",
            location="Manchester",
            date=current_date,
            start_time=current_time,
            event_type="sports",
            keyword="chess",
            is_free=True,
            member_only=False,
            capacity=100,
            fee=Decimal("0.00")
        )

    def test_event_creation(self):
        """Test if an event is created with the correct values."""
        self.assertEqual(self.event.name, "Chess Tournament")
        self.assertEqual(self.event.event_type, "sports")
        self.assertTrue(self.event.is_free)
        self.assertFalse(self.event.member_only)
        self.assertEqual(self.event.capacity, 100)

    def test_str_representation(self):
        """Test the __str__ method of the Event model."""
        expected_str = f"{self.event.name} - {self.event.event_type}"
        self.assertEqual(str(self.event), expected_str)

    def test_fee_validation(self):
        """Test that fee cannot be negative."""
        with self.assertRaises(ValidationError):
            self.event.fee = Decimal("-10.00")
            self.event.full_clean()

    def test_capacity_validation(self):
        """Test that capacity cannot be negative or zero."""
        with self.assertRaises(ValidationError):
            self.event.capacity = 0
            self.event.full_clean()

    def test_society_association(self):
        """Test that an event can be associated with a society."""
        self.event.societies.add(self.test_society)
        self.assertEqual(self.event.societies.first(), self.test_society)

    def test_end_time_validation(self):
        """Test that end_time must be after start_time."""
        current_time = timezone.now().time()
        with self.assertRaises(ValidationError):
            event = Event(
                name="Invalid Time Event",
                description="End time before start time",
                location="London",
                date=timezone.now().date() + timezone.timedelta(days=1),
                start_time=current_time,
                end_time=current_time,
                event_type="social",
                keyword="time"
            )
            event.full_clean()

    def test_multiple_societies(self):
        """Test that an event can be associated with multiple societies."""
        second_society = Society.objects.create(
            name="Drama Club",
            description="A club for drama enthusiasts",
            society_type="arts",
            status="approved",
            manager=self.user
        )
        self.event.societies.add(self.test_society, second_society)
        self.assertEqual(self.event.societies.count(), 2)

    def test_end_time_optional(self):
        """Test that end_time is optional."""
        event = Event.objects.create(
            name="Quick Meeting",
            description="Brief team sync",
            location="Online",
            date=timezone.now().date() + timezone.timedelta(days=1),
            start_time=timezone.now().time(),
            event_type="social",
            keyword="meeting",
            is_free=True,
            member_only=False,
            fee=Decimal("0.00")
        )
        self.assertIsNone(event.end_time)

    def test_cascade_deletion(self):
        """Test that registrations are deleted when event is deleted."""
        event_id = self.event.id
        self.event.delete()
        self.assertEqual(EventRegistration.objects.filter(event_id=event_id).count(), 0)

    def test_invalid_status(self):
        """Test that invalid registration status is rejected."""
        with self.assertRaises(ValidationError):
            registration = EventRegistration(
                event=self.event,
                user=self.user,
                status='invalid_status'
            )
            registration.full_clean()

class EventRegistrationModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="john.doe@university.ac.uk",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="testpassword123"
        )

        self.event = Event.objects.create(
            name="Art Workshop",
            description="Learn to paint",
            location="Online",
            date=timezone.now() + timezone.timedelta(days=3),
            event_type="arts",
            keyword="painting",
            is_free=False,
            member_only=True,
            capacity=50,
            fee=Decimal("10.00")
        )

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
        expected_str = f"{self.registration.user} - {self.registration.event} - {self.registration.status}"
        self.assertEqual(str(self.registration), expected_str)
