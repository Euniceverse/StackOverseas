from django.test import TestCase
from django.utils.timezone import now, timedelta
from apps.events.models import Event
from apps.news.models import News
from apps.societies.models import Society
from filters import EventFilter, DATE_FILTER_CHOICES, NewsFilter

class GlobalFilterSetTest(TestCase):
    def setUp(self):
        self.society = Society.objects.create(name="Test Society", status="approved")
        self.event1 = Event.objects.create(
            name="Free Event",
            price_range=0,
            date_updated=now().date(),
            members_count=10,
            max_capacity=20,
            society=self.society
        )
        self.event2 = Event.objects.create(
            name="Paid Event",
            price_range=50,
            date_updated=now().date() - timedelta(days=10),
            members_count=20,
            max_capacity=20,
            society=self.society
        )
        self.event3 = Event.objects.create(
            name="Future Event",
            price_range=100,
            date_updated=now().date() - timedelta(days=30),
            members_count=5,
            max_capacity=10,
            society=self.society
        )
        self.event4 = Event.objects.create(
            name="Missing Price Event",
            price_range=None,
            date_updated=now().date() - timedelta(days=15),
            members_count=5,
            max_capacity=15,
            society=self.society
        )
    
    def test_filter_by_date(self):
        """Test filtering by date categories"""
        for key, value in DATE_FILTER_CHOICES.items():
            filtered = EventFilter({}, queryset=Event.objects.all()).filter_by_date(Event.objects.all(), 'date', key)
            self.assertTrue(all(event.date_updated >= value for event in filtered), f"Failed for {key}")
    
    def test_filter_by_invalid_date(self):
        """Test filtering with an invalid date category"""
        filtered = EventFilter({}, queryset=Event.objects.all()).filter_by_date(Event.objects.all(), 'date', 'invalid_date')
        self.assertEqual(filtered.count(), Event.objects.count())  # Should return all events

    def test_filter_has_space(self):
        """Test filtering events that have available space"""
        filtered = EventFilter({}, queryset=Event.objects.all()).filter_has_space(Event.objects.all(), 'has_space', True)
        self.assertIn(self.event1, filtered)
        self.assertIn(self.event3, filtered)
        self.assertIn(self.event4, filtered)
        self.assertNotIn(self.event2, filtered)  # event2 is at full capacity

    def test_filter_is_free(self):
        """Test filtering free events"""
        filtered = EventFilter({}, queryset=Event.objects.all()).filter_is_free(Event.objects.all(), 'is_free', True)
        self.assertIn(self.event1, filtered)
        self.assertNotIn(self.event2, filtered)
        self.assertNotIn(self.event3, filtered)
        self.assertNotIn(self.event4, filtered)  # Missing price shouldn't be considered free
    
    def test_filter_missing_price(self):
        """Test filtering events where price is missing"""
        filtered = EventFilter({}, queryset=Event.objects.all()).filter_is_free(Event.objects.all(), 'is_free', True)
        self.assertNotIn(self.event4, filtered)  # Ensure missing price does not count as free


class NewsFilterTest(TestCase):
    def setUp(self):
        self.society1 = Society.objects.create(name="Tech Society", status="approved", society_type="Tech")
        self.society2 = Society.objects.create(name="Art Society", status="approved", society_type="Art")
        
        self.news1 = News.objects.create(
            title="Tech News Today",
            date_posted=now().date(),
            society=self.society1
        )
        self.news2 = News.objects.create(
            title="Old Tech News",
            date_posted=now().date() - timedelta(days=30),
            society=self.society1
        )
        self.news3 = News.objects.create(
            title="Art News Update",
            date_posted=now().date() - timedelta(days=10),
            society=self.society2
        )
    
    def test_filter_by_society_type(self):
        """Test filtering news by society type"""
        filtered = NewsFilter({}, queryset=News.objects.all()).filter_by_society_type(News.objects.all(), 'society_type', "Tech")
        self.assertIn(self.news1, filtered)
        self.assertIn(self.news2, filtered)
        self.assertNotIn(self.news3, filtered)
    
    def test_filter_by_invalid_society_type(self):
        """Test filtering news by an invalid society type"""
        filtered = NewsFilter({}, queryset=News.objects.all()).filter_by_society_type(News.objects.all(), 'society_type', "Science")
        self.assertEqual(filtered.count(), 0)  # No news should match
    
    def test_filter_by_date(self):
        """Test filtering news by date categories"""
        for key, value in DATE_FILTER_CHOICES.items():
            filtered = NewsFilter({}, queryset=News.objects.all()).filter_by_date(News.objects.all(), 'date', key)
            self.assertTrue(all(news.date_posted >= value for news in filtered), f"Failed for {key}")
    
    def test_filter_by_invalid_date(self):
        """Test filtering news with an invalid date category"""
        filtered = NewsFilter({}, queryset=News.objects.all()).filter_by_date(News.objects.all(), 'date', 'invalid_date')
        self.assertEqual(filtered.count(), News.objects.count())  # Should return all news
