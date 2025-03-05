from django.test import TestCase
from django.urls import reverse, resolve
from societies.views import societiespage

class SocietiesUrlsTest(TestCase):
    def test_societies_url_resolves(self):
        """Test if /societies/ resolves to the correct view"""
        url = reverse('societiespage')
        self.assertEqual(resolve(url).func, societiespage)


from django.test import TestCase, Client
from django.urls import reverse, resolve
from apps.societies.views import societiespage, create_society, join_society, delete_society

class SocietiesUrlsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_societies_url_resolves(self):
        url = reverse('societiespage')
        self.assertEqual(resolve(url).func, societiespage)

    def test_create_society_url_resolves(self):
        url = reverse('society-create')
        self.assertEqual(resolve(url).func, create_society)

    def test_join_society_url_resolves(self):
        url = reverse('society-join', args=[1])
        self.assertEqual(resolve(url).func, join_society)

    def test_delete_society_url_resolves(self):
        url = reverse('society-delete', args=[1])
        self.assertEqual(resolve(url).func, delete_society)

    def test_protected_route_requires_login(self):
        response = self.client.get(reverse('society-create'))
        self.assertNotEqual(response.status_code, 200)  # Expect redirect to login

    def test_404_on_invalid_url(self):
        response = self.client.get('/invalid-url/')
        self.assertEqual(response.status_code, 404)

