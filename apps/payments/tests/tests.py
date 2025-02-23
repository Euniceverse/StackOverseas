from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.societies.models import Society
from apps.events.models import Event
from apps.payments.models import Payment
from decimal import Decimal

class PaymentViewsTestCase(TestCase):
    def setUp(self):
        """
        Setup test data: create a user, society, event, and payment records.
        """
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="securepassword"
        )
        self.society = Society.objects.create(
            name="Test Society",
            description="A sample society",
            manager=self.user,
            status="approved"
        )
        self.event = Event.objects.create(
            name="Test Event",
            description="Sample event description",
            event_type="academic",
            location="University Hall",
            fee=Decimal("5.00"),
            society=self.society
        )
    
    def test_payment_view_for_society_membership(self):
        """
        Ensure users can access the payment page for society membership.
        """
        self.client.login(email="testuser@example.com", password="securepassword")
        url = reverse("process_payment", kwargs={"type": "society", "id": self.society.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Payment for Society Membership")

    def test_payment_view_for_event_registration(self):
        """
        Ensure users can access the payment page for event registration.
        """
        self.client.login(email="testuser@example.com", password="securepassword")
        url = reverse("process_payment", kwargs={"type": "event", "id": self.event.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Payment for Event Registration")

    def test_successful_payment_redirect(self):
        """
        Ensure successful payment redirects to the confirmation page.
        """
        self.client.login(email="testuser@example.com", password="securepassword")
        url = reverse("payment_success")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thank you for your payment!")

    def test_payment_failure_redirect(self):
        """
        Ensure payment failure redirects properly.
        """
        self.client.login(email="testuser@example.com", password="securepassword")
        url = reverse("payment_failed")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Payment Failed")