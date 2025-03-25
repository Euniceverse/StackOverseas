from django.test import SimpleTestCase
from django.urls import reverse, resolve
from apps.payments import views

class PaymentsUrlsTests(SimpleTestCase):

    def test_create_checkout_session_url(self):
        url = reverse('payments:create_checkout_session')
        self.assertEqual(url, '/payments/checkout/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.create_checkout_session)

    def test_payment_success_url(self):
        url = reverse('payments:payment_success')
        self.assertEqual(url, '/payments/success/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.payment_success)

    def test_payment_cancel_url(self):
        url = reverse('payments:payment_cancel')
        self.assertEqual(url, '/payments/cancel/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.payment_cancel)