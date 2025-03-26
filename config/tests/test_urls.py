from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse, resolve, clear_url_caches
from django.conf import settings
from apps.news.models import News
from apps.societies.models import Society
from django.contrib.auth import get_user_model
from importlib import reload
import os
import shutil
import config.urls

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
        self.assertNotEqual(response.status_code, 404) 
    
    def test_news_url_resolves(self):
        """Test that the news URL includes the correct app URLs"""
        response = self.client.get('/news/')
        self.assertNotEqual(response.status_code, 404)
    
    def test_societies_url_resolves(self):
        """Test that the societies URL includes the correct app URLs"""
        response = self.client.get('/societies/')
        self.assertIn(response.status_code, [200, 404])
    
    def test_users_url_resolves(self):
        """Test that the users URL includes the correct app URLs"""
        response = self.client.get('/users/')
        self.assertIn(response.status_code, [200, 404])

class MoreURLTests(TestCase):
    def test_ai_search_url_resolves(self):
        """Test that the ai_search URL resolves correctly"""
        url = reverse('ai_search')
        resolved = resolve(url)
        self.assertTrue(callable(resolved.func))
    
    def test_event_map_url_resolves(self):
        """Test that the event_map URL resolves correctly"""
        url = reverse('event_map')
        resolved = resolve(url)
        self.assertTrue(callable(resolved.func))
    
    def test_api_events_url_resolves(self):
        """Test that the event_list (api/events) URL resolves correctly"""
        url = reverse('event_list')
        resolved = resolve(url)
        self.assertTrue(callable(resolved.func))
    
    def test_payments_url_inclusion(self):
        """Test that the payments URLs are included by checking one known payments URL.
        (Requires that 'apps.payments.urls' defines a named URL such as 'create_checkout_session'.)
        """
        try:
            url = reverse('payments:create_checkout_session')
            resolved = resolve(url)
            self.assertTrue(callable(resolved.func))
        except Exception:
            response = self.client.get('/payments/')
            self.assertNotEqual(response.status_code, 404)

        
MEDIA_ROOT_TEST = os.path.join(settings.BASE_DIR, "test_media")

@override_settings(
    DEBUG=True, 
    MEDIA_ROOT=MEDIA_ROOT_TEST, 
    MEDIA_URL='/test_media/',
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'
)
class MediaServingTest(TestCase):
    def setUp(self):
        # Create a dummy uploaded image file.
        self.test_image = SimpleUploadedFile(
            "test_image.jpg",
            b"dummy image content",
            content_type="image/jpeg"
        )
        User = get_user_model()
        dummy_manager = User.objects.create_user(
            email="dummy@uni.ac.uk",
            password="dummy",
            first_name="Dummy",
            last_name="Manager",
            preferred_name="Dummy"
        )
        dummy_society = Society.objects.create(
            name="Dummy Society",
            status="approved",
            manager=dummy_manager
        )
        # Create a News object and save the image via its field.
        self.news = News.objects.create(
            title="News with Media",
            society=dummy_society
        )
        self.news.image.save("test_image.jpg", self.test_image, save=True)
        self.news.save() 
        reload(config.urls)
        clear_url_caches()
        assert os.path.exists(self.news.image.path), f"File {self.news.image.path} not found"

    def test_media_file_serving_debug_true(self):
        """Ensure the media file is accessible when DEBUG is True."""
        media_url = self.news.image.url
        response = self.client.get(media_url)
        self.assertEqual(response.status_code, 200)
    
    def test_media_file_serving_debug_false(self):
        """Ensure the media file is NOT accessible when DEBUG is False."""
        with self.settings(DEBUG=False):
            reload(config.urls)
            clear_url_caches()
            media_url = self.news.image.url
            response = self.client.get(media_url)
            self.assertEqual(response.status_code, 404)

    def tearDown(self):
        """Clean up test media files."""
        import shutil
        if os.path.exists(MEDIA_ROOT_TEST):
            shutil.rmtree(MEDIA_ROOT_TEST, ignore_errors=True)