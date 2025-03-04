from django.test import TestCase
from django.utils import timezone
from apps.events.models import Event, EventRegistration
from apps.events.filters import EventFilter
from apps.societies.models import Society
from datetime import timedelta

class EventFilterTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            email='manager@filters.ac.uk',
            first_name='Filter',
            last_name='Manager',
            preferred_name='FM',
            password='pass123'
        )

        self.society = Society.objects.create(
            name="TestSoc",
            manager=self.manager,  # just a dummy manager
            status="approved",
            society_type="academic"
        )
        # Create some events
        now = timezone.now()
        self.event1 = Event.objects.create(
            name="Event1",
            description="desc1",
            date=now + timedelta(days=1),
            event_type="sports",
            keyword="fun",
            location="London",
            capacity=100,
            fee=0,
            is_free=True
        )
        self.event2 = Event.objects.create(
            name="Event2",
            description="desc2",
            date=now + timedelta(days=2),
            event_type="academic",
            keyword="study",
            location="Manchester",
            capacity=50,
            fee=10,
            is_free=False
        )
        # Add registrations to test capacity logic
        # event2 is partly full
        for i in range(3):
            EventRegistration.objects.create(
                event=self.event2,
                user_id=i+99,  # fake user IDs
                status='accepted'
            )

    def test_event_type_filter(self):
        """Check filtering by event_type."""
        qs = Event.objects.all()
        data = {"event_type": "sports"}
        filtered = EventFilter(data=data, queryset=qs).qs
        self.assertIn(self.event1, filtered)
        self.assertNotIn(self.event2, filtered)

    def test_member_only_filter(self):
        """
        We do not have 'member_only' in these events, but let's test the param usage.
        event1.member_only = False, event2.member_only = False
        """
        qs = Event.objects.all()
        data = {"member_only": True}
        filtered = EventFilter(data=data, queryset=qs).qs
        self.assertEqual(filtered.count(), 0)  # none are True

    def test_fee_min_max_filter(self):
        qs = Event.objects.all()
        data = {"fee_min": 5, "fee_max": 15}
        filtered = EventFilter(data=data, queryset=qs).qs
        # event2 has fee=10
        self.assertIn(self.event2, filtered)
        self.assertNotIn(self.event1, filtered)

    def test_location_filter(self):
        qs = Event.objects.all()
        data = {"location": "London"}
        filtered = EventFilter(data=data, queryset=qs).qs
        self.assertIn(self.event1, filtered)
        self.assertNotIn(self.event2, filtered)

    def test_availability_filter_available(self):
        """
        'available' means capacity is not null, and number of registrations < capacity.
        event2 capacity=50, but only 3 regs => still < 50 => 'available'
        """
        qs = Event.objects.all()
        data = {"availability": "available"}
        filtered = EventFilter(data=data, queryset=qs).qs
        self.assertIn(self.event2, filtered)  
        self.assertIn(self.event1, filtered)  # event1 has 0 regs, capacity=100

    def test_availability_filter_full(self):
        """
        'full' means reg_count == capacity
        We'll manipulate event1 to be 'full' with capacity=2, and create 2 regs
        """
        self.event1.capacity = 2
        self.event1.save()
        EventRegistration.objects.create(event=self.event1, user_id=200, status='accepted')
        EventRegistration.objects.create(event=self.event1, user_id=201, status='accepted')
        qs = Event.objects.all()
        data = {"availability": "full"}
        filtered = EventFilter(data=data, queryset=qs).qs
        self.assertIn(self.event1, filtered)
        self.assertNotIn(self.event2, filtered)

    def test_availability_filter_waiting(self):
        """
        'waiting' => capacity is not null and reg_count > capacity
        We'll add extra registrations to event2 to exceed capacity
        """
        self.event2.capacity = 4
        self.event2.save()
        for i in range(2):  # event2 had 3, add 2 => total 5
            EventRegistration.objects.create(
                event=self.event2,
                user_id=300+i,
                status='accepted'
            )
        qs = Event.objects.all()
        data = {"availability": "waiting"}
        filtered = EventFilter(data=data, queryset=qs).qs
        self.assertIn(self.event2, filtered)

    def test_availability_invalid_value(self):
        """
        If availability=someinvalid => no filter applied => get all
        """
        qs = Event.objects.all()
        data = {"availability": "random"}
        filtered = EventFilter(data=data, queryset=qs).qs
        self.assertEqual(filtered.count(), 2)