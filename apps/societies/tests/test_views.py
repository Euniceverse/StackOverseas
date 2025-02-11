from django.test import TestCase, Client
from django.urls import reverse
from societies.models import Society

class SocietiesViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test societies
        self.society1 = Society.objects.create(name="Tech Club", description="A club for tech enthusiasts.")
        self.society2 = Society.objects.create(name="Art Society", description="A place for art lovers.")

    def test_societies_page_status_code(self):
        """Test if /societies/ page loads correctly"""
        response = self.client.get(reverse('societiespage'))
        self.assertEqual(response.status_code, 200)  # Should return HTTP 200 OK

    def test_template_used(self):
        """Test if the correct template is used"""
        response = self.client.get(reverse('societiespage'))
        self.assertTemplateUsed(response, 'societies.html')

    def test_societies_in_context(self):
        """Test if societies are passed to the template"""
        response = self.client.get(reverse('societiespage'))
        self.assertEqual(len(response.context['societies']), 2)  # Expecting 2 test societies
        self.assertIn(self.society1, response.context['societies'])
        self.assertIn(self.society2, response.context['societies'])
