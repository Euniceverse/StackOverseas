from django.test import TestCase
from django.utils import timezone
from apps.news.models import News, upload_to
from apps.events.models import Event
from apps.societies.models import Society
from apps.users.models import CustomUser
import os

class NewsModelTests(TestCase):
    """Tests for the News model"""

    def setUp(self):
        """Set up test news objects"""
        # create a valid manager 
        self.manager = CustomUser.objects.create_user(
            email="manager@ac.uk",
            first_name="Manager",
            last_name="User",
            preferred_name="Manager",
            password="password123"
        )
        
        # create Society instances.
        self.society1 = Society.objects.create(
            name="Tech Society",
            description="A society for tech enthusiasts",
            society_type="Technology",
            manager=self.manager,  
            location="Campus",
            members_count=0,
            price_range=0.00,
            membership_request_required=False,
            visibility="Private"  
        )
        
        self.society2 = Society.objects.create(
            name="Hidden Society",
            description="A hidden society for testing.",
            society_type="Technology",
            manager=self.manager,
            location="Campus",
            members_count=0,
            price_range=0.00,
            membership_request_required=False,
            visibility="Private"
        )
        
        # create Event instance
        self.event = Event.objects.create(
            name="LinkedEvent",
            date=timezone.now()
        )
        
        # create News instances
        self.news1 = News.objects.create(
            title="Published News",
            content="This is a test news article.",
            society=self.society1,
            event=self.event,
            date_posted=timezone.now(),
            is_published=True
        )

        self.news2 = News.objects.create(
            title="Unpublished News",
            content="This news should not be publicly visible.",
            society=self.society2,
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
        
    def test_get_event_method(self):
        """Test that get_event() retrieves the linked event."""
        linked_events = self.news1.get_event()
        self.assertEqual(len(linked_events), 1)
        self.assertEqual(linked_events.first(), self.event)
        
    def test_upload_to_function(self):
        """Check the upload_to path structure."""
        filename = "myimage.png"
        path = upload_to(self.news1, filename)
        self.assertIn("news_images/", path)
        self.assertTrue(path.endswith("_myimage.png"))
        # example: news_images/20250101120000_myimage.png
        self.assertTrue(path.startswith("news_images/"))
        self.assertIn("_myimage.png", path)