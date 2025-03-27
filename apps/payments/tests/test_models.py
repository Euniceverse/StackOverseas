from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.payments.models import Payment

class PaymentModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="testuser@uni.ac.uk",
            password="password123",
            first_name="Test",
            last_name="User",
            preferred_name="TU"
        )

    def test_str_method_pending(self):
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal("100.00"),
            status="pending",
            payment_for="society"
        )
        expected_str = f"Payment {payment.id} - pending (society)"
        self.assertEqual(str(payment), expected_str)

    def test_str_method_paid(self):
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal("50.50"),
            status="paid",
            payment_for="event"
        )
        expected_str = f"Payment {payment.id} - paid (event)"
        self.assertEqual(str(payment), expected_str)

    def test_created_at_auto_now_add(self):
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal("20.00"),
            status="pending",
            payment_for="event"
        )
        self.assertIsNotNone(payment.created_at)

    def test_stripe_charge_id_default(self):
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal("15.00"),
            status="pending",
            payment_for="society"
        )
        self.assertIsNone(payment.stripe_charge_id)

    def test_payment_for_choices(self):
        expected_choices = [("society", "Society"), ("event", "Event")]
        self.assertEqual(Payment.PAYMENT_FOR_CHOICES, expected_choices)