from django.test import TestCase
from django import forms
from apps.events.forms import NewEventForm
from apps.societies.models import Society
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()

class NewEventFormTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='manager1@forms.ac.uk',
            first_name='Manager1',
            last_name='FormsTest',
            preferred_name='Mgr1',
            password='pass1'
        )
        self.user2 = User.objects.create_user(
            email='manager2@forms.ac.uk',
            first_name='Manager2',
            last_name='FormsTest',
            preferred_name='Mgr2',
            password='pass2'
        )

        self.soc1 = Society.objects.create(
            name="Soc1",
            description="desc",
            society_type="academic",
            manager=self.user1,
            status="approved"
        )
        self.soc2 = Society.objects.create(
            name="Soc2",
            description="desc2",
            society_type="sports",
            manager=self.user2,
            status="approved"
        )

    def test_valid_data_is_free_fee_logic(self):
        """
        If fee > 0 => is_free = False
        If fee=0 => is_free = True
        Must pass for society choices, etc.
        """
        form_data = {
            "name": "Event Name",
            "description": "Some desc",
            "event_type": "sports",
            "date": "2025-05-10T10:00",
            "keyword": "fun",
            "location": "Online",
            "capacity": "50",
            "member_only": False,
            "fee": "0.00",
            "is_free": True,
            "latitude": "51.5074",
            "longitude": "-0.1278"
        }
        form = NewEventForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        cleaned = form.clean()
        self.assertTrue(cleaned["is_free"])
        # If we set fee=10 => is_free => false
        form_data["fee"] = "10.00"
        form2 = NewEventForm(data=form_data)
        self.assertTrue(form2.is_valid())
        cleaned2 = form2.clean()
        self.assertFalse(cleaned2["is_free"])

    def test_missing_fields(self):
        """Check required fields cause errors."""
        form_data = {}
        form = NewEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("description", form.errors)
        self.assertIn("date", form.errors)
        self.assertIn("event_type", form.errors)
        self.assertIn("location", form.errors)

    def test_capacity_min_value(self):
        """capacity must be >= 1 if provided."""
        form_data = {
            "name": "TestEvent",
            "description": "Desc",
            "event_type": "sports",
            "date": "2025-05-01T09:00",
            "keyword": "x",
            "location": "Somewhere",
            "member_only": True,
            "fee": "0.00",
            "is_free": True,
            "capacity": "0"  # invalid
        }
        form = NewEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("capacity", form.errors)

    def test_date_format(self):
        """Check that an invalid date raises error."""
        form_data = {
            "name": "Bad Date",
            "description": "Desc",
            "event_type": "sports",
            "date": "notadate",
            "keyword": "k",
            "location": "Loc",
            "capacity": "10",
            "member_only": False,
            "fee": "0.00",
            "is_free": True,
        }
        form = NewEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)