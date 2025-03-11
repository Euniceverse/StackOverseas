from django.test import TestCase, Client
from django.urls import reverse, resolve
from apps.societies.views import societiespage, create_society, join_society, admin_confirm_delete

class SocietiesUrlsTest(TestCase):
    """Tests for Societies URLs."""
    def setUp(self):
        """Setup for tests."""
        self.client = Client()
        
    def test_societies_url_resolves(self):
        """Test that the 'societiespage' URL resolves to the correct view."""
        url = reverse('societiespage')
        self.assertEqual(resolve(url).func, societiespage)

    def test_create_society_url_resolves(self):
        """Test that the create_society URL resolves to the create_society view."""
        url = reverse('create_society')
        self.assertEqual(resolve(url).func, create_society)

    def test_join_society_url_resolves(self):
        """Test that the join_society URL resolves to the join_society view."""
        url = reverse('join_society', args=[1])
        self.assertEqual(resolve(url).func, join_society)

    def test_delete_society_url_resolves(self):
        """Test that the admin_confirm_delete URL resolves to the delete_society view."""
        url = reverse('admin_confirm_delete', args=[1])
        self.assertEqual(resolve(url).func, admin_confirm_delete)

    def test_protected_route_requires_login(self):
        """Test that the create_society route requires login (non-authenticated user is redirected)."""
        response = self.client.get(reverse('create_society'))
        self.assertNotEqual(response.status_code, 200)
        
    def test_404_on_invalid_url(self):
        """Test that an invalid URL returns a 404 status."""
        response = self.client.get('/invalid-url/')
        self.assertEqual(response.status_code, 404)

