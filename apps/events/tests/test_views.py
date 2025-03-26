from django.test import TestCase, Client
from django.urls import reverse
from apps.events.models import Event
from apps.news.models import News
from django.utils import timezone
from apps.events.views import eventspage, auto_edit_news
from django.contrib.auth import get_user_model
from apps.societies.models import Society, Membership, MembershipRole, MembershipStatus
from apps.news.models import News
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from apps.events.models import Event

User = get_user_model()

class EventPageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('eventspage')
        self.some_user = User.objects.create_user(
            email='someuser1@ex.com',
            first_name='Some1',
            last_name='Ex1',
            preferred_name='S1',
            password='pass123'
        )
        self.some_soc = Society.objects.create(
            name="NewsSoc", manager=self.some_user, status="approved", society_type="sports"
        )
        News.objects.create(
            title="EventPage News 1",
            content="Content1",
            is_published=True,
            society=self.some_soc
        )

        self.some_user2 = User.objects.create_user(
            email='someuser2@ex.com',
            first_name='Some2',
            last_name='Ex2',
            preferred_name='S2',
            password='pass456'
        )
        self.some_soc2 = Society.objects.create(
            name="NewsSoc2", manager=self.some_user2, status="approved", society_type="sports"
        )
        News.objects.create(
            title="EventPage News 2",
            content="Content2",
            is_published=True,
            society=self.some_soc2
        )

    def test_eventspage_renders(self):
        """Check that eventspage returns 200 and uses events.html."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events.html')
        # Should show the news
        self.assertIn("news_list", response.context)
        self.assertEqual(len(response.context["news_list"]), 2)


class EventListAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('event-list')
        # create some events
        now = timezone.now()
        e1 = Event.objects.create(
            name="API Event1",
            date=now + timedelta(days=1),
            event_type="sports",
            location="Online"
        )
        e2 = Event.objects.create(
            name="API Event2",
            date=now + timedelta(days=5),
            event_type="arts",
            location="London"
        )

    def test_list_api(self):
        """Check that the API returns future events in JSON."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(isinstance(data, list))
        self.assertTrue(len(data) >= 2, data)

    def test_search_filter(self):
        """Test the ?search= param (search_fields = name, description)."""
        response = self.client.get(self.url, {"search": "API Event1"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "API Event1")


class AutoEditNewsViewEdgeCaseTest(TestCase):
    """We covered the main flow in test_create_event_flow, 
       but let's do an extra check if no news is found or partial formset data.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            email='editor@uni.ac.uk',
            first_name='Ed',
            last_name='Test',
            preferred_name='EdT',
            password='pass'
        )
        self.client = Client()
        self.client.login(email='editor@uni.ac.uk', password='pass')
        self.event = Event.objects.create(
            name="NoNewsEvent",
            date=timezone.now() + timedelta(days=2),
            event_type="social",
            location="Main Hall"
        )
        self.test_society = Society.objects.create(
            name="TestSociety",
            manager=self.user,
            status="approved",
            society_type="other"
        )
        self.url = reverse('auto_edit_news', args=[self.event.id])

    def test_no_news_found(self):
        """If there's no news for this event, formset is empty but page loads."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form-TOTAL_FORMS")

    def test_partial_post(self):
        """If we post partial data to the formset, it should fail validation."""
        # Create one news item
        news = News.objects.create(
            title="AutoNews",
            society=self.test_society,
            event=self.event,
            is_published=False
        )
        response = self.client.post(self.url, {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-0-id': str(news.id),
            # Missing required fields like 'title' if your actual form requires them
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required", status_code=200)
        # The news object is still not published
        news.refresh_from_db()
        self.assertFalse(news.is_published)