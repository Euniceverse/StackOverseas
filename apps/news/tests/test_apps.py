
from django.test import TestCase
from django.apps import apps
from apps.news.apps import NewsConfig

class NewsConfigTest(TestCase):
    def test_news_config(self):
        """Ensure the News app config is correct."""
        self.assertEqual(NewsConfig.name, 'apps.news')
        # Also check that Django can retrieve this config by label:
        self.assertEqual(apps.get_app_config('news').name, 'apps.news')