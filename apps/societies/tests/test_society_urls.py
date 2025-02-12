from django.test import TestCase
from django.urls import reverse, resolve
from societies.views import societiespage

class SocietiesUrlsTest(TestCase):
    def test_societies_url_resolves(self):
        """Test if /societies/ resolves to the correct view"""
        url = reverse('societiespage')
        self.assertEqual(resolve(url).func, societiespage)
