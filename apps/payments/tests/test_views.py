import json
from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from django.shortcuts import render
from unittest.mock import patch, MagicMock

# Import the views module from your payments app
from apps.payments import views


class PaymentsViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('apps.payments.views.stripe.checkout.Session.create')
    def test_create_checkout_session_event_success(self, mock_session_create):
        # Simulate a session object with a url attribute
        mock_session = MagicMock()
        mock_session.url = 'http://dummy-session-url.com'
        mock_session_create.return_value = mock_session

        # Create a POST request for an 'event' payment
        post_data = {
            'type': 'event',
            'id': '123',
            'name': 'Test Event',
            'price': '10',
            'description': 'Test Description'
        }
        request = self.factory.post('/payments/create/', data=post_data)

        # Call the view
        response = views.create_checkout_session(request)

        # Assert that the response is a JsonResponse with the session URL
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode())
        self.assertIn('url', response_data)
        self.assertEqual(response_data['url'], mock_session.url)

        # Verify that stripe.checkout.Session.create was called with expected parameters\n
        expected_success_url = f"http://127.0.0.1:8000/payments/success/?event_id=123"
        mock_session_create.assert_called_once()
        call_args = mock_session_create.call_args[1]
        self.assertEqual(call_args.get('mode'), 'payment')
        self.assertEqual(call_args.get('success_url'), expected_success_url)

    @patch('apps.payments.views.stripe.checkout.Session.create')
    def test_create_checkout_session_society_success(self, mock_session_create):
        # Simulate a session object with a url attribute
        mock_session = MagicMock()
        mock_session.url = 'http://dummy-session-url.com'
        mock_session_create.return_value = mock_session

        # Create a POST request for a 'society' payment
        post_data = {
            'type': 'society',
            'id': '456',
            'name': 'Test Society',
            'price': '20',
            'description': 'Society Description'
        }
        request = self.factory.post('/payments/create/', data=post_data)

        # Call the view
        response = views.create_checkout_session(request)

        # For society payments, the view should return a redirect\n
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, mock_session.url)

        expected_success_url = f"http://127.0.0.1:8000/payments/success/?type=society&id=456"
        mock_session_create.assert_called_once()
        call_args = mock_session_create.call_args[1]
        self.assertEqual(call_args.get('success_url'), expected_success_url)

    def test_create_checkout_session_invalid_payment_type(self):
        # Create a POST request with an invalid payment type\n
        post_data = {
            'type': 'invalid',
            'id': '789'
        }
        request = self.factory.post('/payments/create/', data=post_data)

        response = views.create_checkout_session(request)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode())
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Invalid payment type')

    def test_create_checkout_session_non_post(self):
        # Create a GET request instead of POST\n
        request = self.factory.get('/payments/create/')

        response = views.create_checkout_session(request)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode())
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Invalid request')

    @patch('apps.payments.views.stripe.checkout.Session.create')
    def test_create_checkout_session_exception(self, mock_session_create):
        # Simulate an exception during session creation\n
        mock_session_create.side_effect = Exception('Stripe error')

        post_data = {
            'type': 'event',
            'id': '123',
            'name': 'Test Event',
            'price': '10',
            'description': 'Test Description'
        }
        request = self.factory.post('/payments/create/', data=post_data)

        response = views.create_checkout_session(request)

        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content.decode())
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Stripe error')

    def test_payment_success(self):
        response = self.client.get('/payments/success/', {'type': 'event', 'id': '123'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('type', response.context)
        self.assertIn('id', response.context)
        self.assertEqual(response.context['type'], 'event')
        self.assertEqual(response.context['id'], '123')

    @patch('apps.payments.views.get_object_or_404')
    def test_payment_cancel_event(self, mock_get_object_or_404):
        dummy_event = {'id': 123, 'name': 'Dummy Event'}
        mock_get_object_or_404.return_value = dummy_event

        response = self.client.get('/payments/cancel/', {'type': 'event', 'id': '123'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('object', response.context)
        self.assertEqual(response.context['object'], dummy_event)
        self.assertEqual(response.context['type'], 'event')

    @patch('apps.payments.views.get_object_or_404')
    def test_payment_cancel_society(self, mock_get_object_or_404):
        dummy_society = {'id': 456, 'name': 'Dummy Society'}
        mock_get_object_or_404.return_value = dummy_society

        response = self.client.get('/payments/cancel/', {'type': 'society', 'id': '456'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('object', response.context)
        self.assertEqual(response.context['object'], dummy_society)
        self.assertEqual(response.context['type'], 'society')

    def test_payment_cancel_invalid_id(self):
        response = self.client.get('/payments/cancel/', {'type': 'event', 'id': 'abc'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('object', response.context)
        self.assertIsNone(response.context['object'])
        self.assertEqual(response.context['type'], 'event')

    def test_payment_cancel_unknown_type(self):
        response = self.client.get('/payments/cancel/', {'type': 'unknown', 'id': '123'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('object', response.context)
        self.assertIsNone(response.context['object'])
        self.assertEqual(response.context['type'], 'unknown')