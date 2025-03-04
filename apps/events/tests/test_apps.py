from django.test import TestCase
from django.apps import apps
from apps.events.apps import EventsConfig

class EventsConfigTest(TestCase):
    def test_apps_name(self):
        """Check the name attribute."""
        self.assertEqual(EventsConfig.name, "apps.events")

    def test_apps_ready(self):
        """
        The 'ready' method imports signals. 
        We can just call it to ensure no error is raised.
        """
        config = apps.get_app_config('events')
        config.ready()  # Should not raise an exception
        self.assertTrue(True)