from django.contrib import admin
from django.test import SimpleTestCase
from apps.payments.models import Payment

class PaymentAdminTest(SimpleTestCase):
    def test_payment_model_is_registered(self):
        self.assertIn(Payment, admin.site._registry)