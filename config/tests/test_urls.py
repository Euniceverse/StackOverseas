from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse, resolve
from django.conf import settings
from apps.news.models import News
import os

class URLTests(TestCase):
    def test_admin_url_resolves(self):
        """Test that the admin URL is correctly routed"""
        url = reverse('admin:index')
        self.assertEqual(resolve(url).func.__module__, 'django.contrib.admin.sites')
    
    def test_home_url_resolves(self):
        """Test that the home URL resolves correctly"""
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_events_url_resolves(self):
        """Test that the events URL includes the correct app URLs"""
        response = self.client.get('/events/')
        self.assertNotEqual(response.status_code, 404)  # Ensure it doesn't return a 404
    
    def test_news_url_resolves(self):
        """Test that the news URL includes the correct app URLs"""
        response = self.client.get('/news/')
        self.assertNotEqual(response.status_code, 404)
    
    def test_societies_url_resolves(self):
        """Test that the societies URL includes the correct app URLs"""
        response = self.client.get('/societies/')
        self.assertNotEqual(response.status_code, 404)
    
    def test_users_url_resolves(self):
        """Test that the users URL includes the correct app URLs"""
        response = self.client.get('/users/')
        self.assertNotEqual(response.status_code, 404)


        
MEDIA_ROOT_TEST = os.path.join(settings.BASE_DIR, "test_media")

@override_settings(MEDIA_ROOT=MEDIA_ROOT_TEST)
class MediaServingTest(TestCase):
    def setUp(self):
        """Create a test media file and a news object referencing it."""
        self.test_image = SimpleUploadedFile(
            "test_image.jpg",
            content=b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00",
            content_type="image/jpeg"
        )
        self.news = News.objects.create(
            title="News with Media",
            image=self.test_image
        )
        self.media_url = f"{settings.MEDIA_URL}test_image.jpg"
        with open(os.path.join(MEDIA_ROOT_TEST, "test_image.jpg"), "wb") as f:
            f.write(self.test_image.read())

    def test_media_file_serving(self):
        """Ensure the media file is accessible at its media URL."""
        media_url = f"{settings.MEDIA_URL}{self.news.image.name}"
        response = self.client.get(media_url)
        if settings.DEBUG:
            self.assertEqual(response.status_code, 200)
        else:
            self.assertEqual(response.status_code, 404)  # Should not be served in production

    def test_media_file_serving_debug_true(self):
        """Ensure the media file is accessible when DEBUG is True."""
        with self.settings(DEBUG=True):
            media_url = f"{settings.MEDIA_URL}{self.news.image.name}"
            response = self.client.get(media_url)
            self.assertEqual(response.status_code, 200)
    
    def test_media_file_serving_debug_false(self):
        """Ensure the media file is NOT accessible when DEBUG is False."""
        with self.settings(DEBUG=False):
            media_url = f"{settings.MEDIA_URL}{self.news.image.name}"
            response = self.client.get(media_url)
            self.assertEqual(response.status_code, 404)

    def tearDown(self):
        """Clean up test media files."""
        if os.path.exists(MEDIA_ROOT_TEST):
            for file in os.listdir(MEDIA_ROOT_TEST):
                os.remove(os.path.join(MEDIA_ROOT_TEST, file))
            os.rmdir(MEDIA_ROOT_TEST)
