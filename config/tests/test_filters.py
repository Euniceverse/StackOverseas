from django.test import TestCase
from django.utils.timezone import now, timedelta
from apps.events.models import Event
from apps.news.models import News
from apps.societies.models import Society
from config.filters import (
    EventFilter, 
    DATE_FILTER_CHOICES, 
    NewsFilter,
    GlobalFilterSet,
    SocietyFilter
)
from django.contrib.auth import get_user_model
from django.db.models import Q, Value

class GlobalFilterSetTest(TestCase):

    def setUp(self):
        User = get_user_model()
        self.manager = User.objects.create_user(
            email="manager@example.com", 
            password="password",
            first_name="Manager1",
            last_name="One",
            preferred_name="Mgr1"
        )
        self.society = Society.objects.create(name="Test Society", status="approved", manager=self.manager)
        self.event1 = Event.objects.create(
            name="Free Event",
            fee=0,
            date=now().date(),
            capacity=20,
        )
        self.event1.society.add(self.society)

        self.event2 = Event.objects.create(
            name="Paid Event",
            fee=50,
            date=now().date() - timedelta(days=10),
            capacity=20,
        )
        self.event2.society.add(self.society)

        self.event3 = Event.objects.create(
            name="Future Event",
            fee=100,
            date=now().date() - timedelta(days=30),
            capacity=10,
        )
        self.event3.society.add(self.society)
    
    def test_filter_by_date(self):
        """Test filtering by date categories"""
        for key, value in DATE_FILTER_CHOICES.items():
            filtered = EventFilter({}, queryset=Event.objects.all()).filter_by_date(
                Event.objects.all(), 'date', key
            )
            self.assertTrue(all(event.date.date() >= value for event in filtered), f"Failed for {key}")

    def test_filter_by_invalid_date(self):
        """Test filtering with an invalid date category"""
        filtered = EventFilter({}, queryset=Event.objects.all()).filter_by_date(
            Event.objects.all(), 'date', 'invalid_date'
        )
        self.assertEqual(filtered.count(), Event.objects.count())

    def test_filter_is_free(self):
        """Test filtering free events"""
        filtered = EventFilter({}, queryset=Event.objects.all()).filter_is_free(
            Event.objects.all(), 'is_free', True
        )
        self.assertIn(self.event1, filtered)
        self.assertNotIn(self.event2, filtered)
        self.assertNotIn(self.event3, filtered)

class NewsFilterTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.manager = User.objects.create_user(
            email="manager2@university.ac.uk", 
            password="password",
            first_name="Manager2",
            last_name="Two",
            preferred_name="Mgr"
        )
        self.society1 = Society.objects.create(name="Tech Society", status="approved", society_type="Tech", manager=self.manager) 
        self.society2 = Society.objects.create(name="Art Society", status="approved", society_type="Art", manager=self.manager)
        
        self.news1 = News.objects.create(
            title="Tech News Today",
            date_posted=now().date(),
            society=self.society1
        )

        self.news2 = News.objects.create(
            title="Old Tech News",
            date_posted=now().date() - timedelta(days=30),
            society=self.society2
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
        self.assertNotIn(self.news2, filtered)
        self.assertNotIn(self.news3, filtered)
    
    def test_filter_by_invalid_society_type(self):
        """Test filtering news by an invalid society type"""
        filtered = NewsFilter({}, queryset=News.objects.all()).filter_by_society_type(News.objects.all(), 'society_type', "Science")
        self.assertEqual(filtered.count(), 0)  # no news should match
    
    def test_filter_by_date(self):
        """Test filtering news by date categories"""
        for key, value in DATE_FILTER_CHOICES.items():
            filtered = NewsFilter({}, queryset=News.objects.all()).filter_by_date(News.objects.all(), 'date', key)
            self.assertTrue(all(news.date_posted.date() >= value for news in filtered), f"Failed for {key}")
    
    def test_filter_by_invalid_date(self):
        """Test filtering news with an invalid date category"""
        filtered = NewsFilter({}, queryset=News.objects.all()).filter_by_date(News.objects.all(), 'date', 'invalid_date')
        self.assertEqual(filtered.count(), News.objects.count())  # should return all news

class EventFilterTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.manager = User.objects.create_user(
            email="manager3@example.com", 
            password="password",
            first_name="Manager3",
            last_name="Three",
            preferred_name="Mgr3"
        )
        self.society = Society.objects.create(
            name="Extra Society", status="approved", manager=self.manager
        )
        self.event_a = Event.objects.create(
            name="Event A",
            fee=30,
            fee_member=25,
            fee_general=35,
            date=now().date(),
            capacity=50,
        )
        self.event_a.society.add(self.society)

        self.event_b = Event.objects.create(
            name="Event B",
            fee=60,
            fee_member=55,
            fee_general=65,
            date=now().date() - timedelta(days=5),
            capacity=50,
        )
        self.event_b.society.add(self.society)

        self.event_c = Event.objects.create(
            name="Event C",
            fee=90,
            fee_member=85,
            fee_general=95,
            date=now().date() - timedelta(days=15),
            capacity=30,
        )
        self.event_c.society.add(self.society)

    def test_filter_by_price_range_both(self):
        """Test EventFilter.filter_by_price when both start and stop are provided"""
        from collections import namedtuple
        Range = namedtuple('Range', ['start', 'stop'])
        price_range = Range(start=20, stop=40)
        qs = Event.objects.all()
        filtered = EventFilter({'price_range': price_range}, queryset=qs).filter_by_price(qs, 'price_range', price_range)
        self.assertIn(self.event_a, filtered)
        self.assertNotIn(self.event_b, filtered)
        self.assertNotIn(self.event_c, filtered)

    def test_filter_by_price_range_start_only(self):
        """Test EventFilter.filter_by_price when only start is provided"""
        from collections import namedtuple
        Range = namedtuple('Range', ['start', 'stop'])
        price_range = Range(start=80, stop=None)
        qs = Event.objects.all()
        filtered = EventFilter({'price_range': price_range}, queryset=qs).filter_by_price(qs, 'price_range', price_range)
        self.assertIn(self.event_c, filtered)
        self.assertNotIn(self.event_a, filtered)
        self.assertNotIn(self.event_b, filtered)

    def test_filter_by_price_range_stop_only(self):
        """Test EventFilter.filter_by_price when only stop is provided"""
        from collections import namedtuple
        Range = namedtuple('Range', ['start', 'stop'])
        price_range = Range(start=None, stop=50)
        qs = Event.objects.all()
        filtered = EventFilter({'price_range': price_range}, queryset=qs).filter_by_price(qs, 'price_range', price_range)
        self.assertIn(self.event_a, filtered)
        self.assertNotIn(self.event_b, filtered)
        self.assertNotIn(self.event_c, filtered)

    def test_filter_available_slots(self):
        """Test EventFilter.filter_available_slots"""
        qs = Event.objects.all()
        filtered_true = EventFilter({}, queryset=qs).filter_available_slots(qs, 'available_slots', True)
        self.assertIn(self.event_a, filtered_true)
        self.assertIn(self.event_b, filtered_true)
        self.assertIn(self.event_c, filtered_true)
        filtered_false = EventFilter({}, queryset=qs).filter_available_slots(qs, 'available_slots', False)
        self.assertEqual(filtered_false.count(), 0)

class SocietyFilterTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.manager = User.objects.create_user(
            email="manager4@example.com", 
            password="password",
            first_name="Manager4",
            last_name="Four",
            preferred_name="Mgr4"
        )
        self.society_a = Society.objects.create(
            name="Alpha Society", status="approved", society_type="Alpha", manager=self.manager
        )
        self.society_b = Society.objects.create(
            name="Beta Society", status="approved", society_type="Beta", manager=self.manager
        )
        self.society_c = Society.objects.create(
            name="Gamma Society", status="approved", society_type="AlphaGamma", manager=self.manager
        )

    def test_society_type_filter(self):
        qs = Society.objects.all()
        filtered = SocietyFilter({}, queryset=qs).qs
        filtered = filtered.filter(society_type__icontains="alpha")
        self.assertIn(self.society_a, filtered)
        self.assertIn(self.society_c, filtered)
        self.assertNotIn(self.society_b, filtered)