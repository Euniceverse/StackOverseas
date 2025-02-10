from django.test import TestCase
from apps.events.forms import NewEventForm
from decimal import Decimal
from apps.societies.models import Society
from django.contrib.auth import get_user_model
from django.utils import timezone
from config.constants import MAX_NAME, MAX_DESCRIPTION, MAX_LOCATION
from django.core.exceptions import ValidationError
from apps.events.models import Event

class NewEventFormTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@university.ac.uk",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="testpass123"
        )

        self.society = Society.objects.create(
            name="Test Society",
            description="Test Description",
            society_type="social",
            status="approved",
            manager=self.user
        )

        self.valid_form_data = {
            'name': 'Test Event',
            'description': 'Test Description',
            'event_type': 'social',
            'date': '2024-03-01 14:00:00',
            'location': 'London',
            'fee': Decimal('0.00'),
            'is_free': True,
            'society': [self.society.id],
            'keyword': 'test',
            'capacity': 50,
            'member_only': False
        }

    def test_valid_form(self):
        """Test form with valid data."""
        form = NewEventForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

    def test_fee_and_is_free_consistency(self):
        """Test that is_free is automatically set to False when fee > 0."""
        form_data = self.valid_form_data.copy()
        form_data['fee'] = Decimal('10.00')
        form = NewEventForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data['is_free'])

    def test_required_fields(self):
        """Test that required fields are enforced."""
        required_fields = ['name', 'description', 'event_type', 'date', 'location', 'society']

        for field in required_fields:
            form_data = self.valid_form_data.copy()
            del form_data[field]
            form = NewEventForm(data=form_data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)

    def test_negative_capacity(self):
        """Test that negative capacity is invalid."""
        form_data = self.valid_form_data.copy()
        form_data['capacity'] = -1
        form = NewEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('capacity', form.errors)

    def test_negative_fee(self):
        """Test that negative fee is invalid."""
        form_data = self.valid_form_data.copy()
        form_data['fee'] = Decimal('-10.00')
        form = NewEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('fee', form.errors)

    def test_optional_fields(self):
        """Test that optional fields can be omitted."""
        optional_fields = ['keyword', 'capacity', 'member_only']
        form_data = self.valid_form_data.copy()

        for field in optional_fields:
            del form_data[field]
            form = NewEventForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Form should be valid without {field}")

    def test_invalid_event_type(self):
        """Test that invalid event type is rejected."""
        form_data = self.valid_form_data.copy()
        form_data['event_type'] = 'invalid_type'
        form = NewEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('event_type', form.errors)

    def test_invalid_date_format(self):
        """Test that invalid date format is rejected."""
        form_data = self.valid_form_data.copy()
        form_data['date'] = 'invalid-date'
        form = NewEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_multiple_society_selection(self):
        """Test that multiple societies can be selected."""
        second_society = Society.objects.create(
            name="Second Society",
            description="Another society",
            society_type="social",
            status="approved",
            manager=self.user
        )
        form_data = self.valid_form_data.copy()
        form_data['society'] = [self.society.id, second_society.id]
        form = NewEventForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_name_max_length(self):
        """Test that name field respects max length."""
        form_data = self.valid_form_data.copy()
        form_data['name'] = 'a' * (MAX_NAME + 1)
        form = NewEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_field_max_lengths(self):
        """Test field max length validations."""
        with self.assertRaises(ValidationError):
            event = Event(
                name="a" * (MAX_NAME + 1),
                description="b" * (MAX_DESCRIPTION + 1),
                location="c" * (MAX_LOCATION + 1),
                date=timezone.now().date() + timezone.timedelta(days=1),
                start_time=timezone.now().time(),
                event_type="social",
                keyword="test"
            )
            event.full_clean()

    def test_description_max_length(self):
        """Test description field max length."""
        form_data = self.valid_form_data.copy()
        form_data['description'] = 'a' * (MAX_DESCRIPTION + 1)
        form = NewEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_location_max_length(self):
        """Test location field max length."""
        form_data = self.valid_form_data.copy()
        form_data['location'] = 'a' * (MAX_LOCATION + 1)
        form = NewEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('location', form.errors)

    def test_invalid_society(self):
        """Test that non-existent society ID is rejected."""
        form_data = self.valid_form_data.copy()
        form_data['society'] = [999]  # Non-existent ID
        form = NewEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('society', form.errors)
