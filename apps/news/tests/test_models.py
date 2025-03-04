from django.test import TestCase
from django.utils import timezone
from apps.news.models import News, upload_to
from apps.events.models import Event
from apps.societies.models import Society
import os

class NewsModelTests(TestCase):
    """Tests for the News model"""

    def setUp(self):
        """Set up test news objects"""
        self.news1 = News.objects.create(
            title="Published News",
            content="This is a test news article.",
            society="Tech Society",
            date_posted=timezone.now(),
            is_published=True
        )

        self.news2 = News.objects.create(
            title="Unpublished News",
            content="This news should not be publicly visible.",
            society="Hidden Society",
            date_posted=timezone.now(),
            is_published=False
        )

    def test_news_creation(self):
        """Test that news objects are created correctly"""
        self.assertEqual(self.news1.title, "Published News")
        self.assertEqual(self.news1.content, "This is a test news article.")
        self.assertTrue(self.news1.is_published)

    def test_published_news_queryset(self):
        """Test that only published news appears in published queries"""
        published_news = News.objects.filter(is_published=True)
        self.assertEqual(published_news.count(), 1)
        self.assertEqual(published_news.first(), self.news1)

    def test_unpublished_news_not_in_queryset(self):
        """Test that unpublished news does not appear in published queries"""
        published_news_titles = list(News.objects.filter(is_published=True).values_list("title", flat=True))
        self.assertNotIn("Unpublished News", published_news_titles)

    def test_news_str_method(self):
        """Test the string representation of news model"""
        self.assertEqual(str(self.news1), "Published News")

class NewsExtraModelTests(TestCase):
    def setUp(self):
        self.society = Society.objects.create(
            name="Event Society",
            description="desc",
            society_type="sports",
            manager_id=10,  # or create real user
            status="approved"
        )
        self.event = Event.objects.create(
            name="LinkedEvent",
            date=timezone.now()
        )
        self.news_item = News.objects.create(
            title="News With Event",
            content="Testing event link",
            society=self.society,
            event=self.event,
            is_published=False
        )

    def test_get_event_method(self):
        """Test that get_event() retrieves the linked event."""
        # your News model says: get_event() -> Event.objects.filter(news=self)
        # but since we used event=... we can confirm if it appears:
        linked_events = self.news_item.get_event()
        self.assertEqual(len(linked_events), 1)
        self.assertEqual(linked_events.first(), self.event)

    def test_upload_to_function(self):
        """Check the upload_to path structure."""
        filename = "myimage.png"
        path = upload_to(self.news_item, filename)
        self.assertIn("news_images/", path)
        self.assertTrue(path.endswith("_myimage.png"))
        # e.g. news_images/20250101120000_myimage.png
        # Just ensure it has the prefix and suffix:
        self.assertTrue(path.startswith("news_images/"))
        self.assertIn("_myimage.png", path)