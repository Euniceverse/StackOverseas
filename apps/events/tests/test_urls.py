from django.test import TestCase
from django.urls import reverse, resolve
from apps.events.views import (
    eventspage,
    create_event,
    auto_edit_news,
    EventListAPIView
)

class EventsURLsTest(TestCase):
    def test_eventspage_url(self):
        """Check that the '' pattern for events resolves to eventspage."""
        url = reverse('eventspage')
        self.assertEqual(resolve(url).func, eventspage)

    def test_eventlist_api_url(self):
        url = reverse('event-list')
        self.assertEqual(resolve(url).func.view_class, EventListAPIView)

    def test_create_event_url(self):
        url = reverse('event_create', args=[123])
        self.assertEqual(resolve(url).func, create_event)

    def test_auto_edit_news_url(self):
        url = reverse('auto_edit_news', args=[456])
        self.assertEqual(resolve(url).func, auto_edit_news)