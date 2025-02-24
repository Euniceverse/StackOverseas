# apps/events/tests/test_create_event_flow.py

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.events.models import Event
from apps.events.forms import NewEventForm
from apps.societies.models import Society, Membership, MembershipRole, MembershipStatus
from apps.news.models import News
from apps.events.models import Host
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class CreateEventViewTests(TestCase):
    """
    Tests the create_event view, including:
    - permission checks (manager/co_manager/editor)
    - successful event creation triggers News creation (is_published=False)
    - final redirect to auto_edit_news
    """

    def setUp(self):
        self.client = Client()
        # Create a Society
        self.society_owner = User.objects.create_user(
            email='owner@uni.ac.uk',
            password='ownerpass'
        )
        self.society = Society.objects.create(
            name='TestSociety',
            manager=self.society_owner,
            status='approved',
            society_type='academic'
        )

        # A manager membership:
        Membership.objects.create(
            society=self.society,
            user=self.society_owner,
            role=MembershipRole.MANAGER,
            status=MembershipStatus.APPROVED
        )

        # Another co-manager user
        self.user_co = User.objects.create_user(
            email='co@uni.ac.uk', password='copass'
        )
        Membership.objects.create(
            society=self.society,
            user=self.user_co,
            role=MembershipRole.CO_MANAGER,
            status=MembershipStatus.APPROVED
        )

        # An editor
        self.user_editor = User.objects.create_user(
            email='editor@uni.ac.uk', password='editpass'
        )
        Membership.objects.create(
            society=self.society,
            user=self.user_editor,
            role=MembershipRole.EDITOR,
            status=MembershipStatus.APPROVED
        )

        # A normal user (no permission)
        self.user_normal = User.objects.create_user(
            email='normal@uni.ac.uk',
            password='normalpass'
        )
        # No membership for them in this society

        self.url = reverse('event_create', args=[self.society.id])

    def test_manager_can_create_event(self):
        self.client.login(email='owner@uni.ac.uk', password='ownerpass')
        data = {
            'name': 'Super Event',
            'description': 'Description here',
            'date': '2025-05-01T10:00',  # format for datetime-local
            'event_type': 'sports',
            'keyword': 'fun',
            'location': 'Campus Hall',
            'capacity': '100',
            'member_only': False,
            'fee': '10.00',
            'is_free': False, 
            # Typically the form's field is "society". It's a CheckboxSelectMultiple or similar.
            'society': [str(self.society.id)]
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Check if event is created
        event_qs = Event.objects.filter(name='Super Event')
        self.assertTrue(event_qs.exists())
        new_event = event_qs.first()

        # We expect redirect to auto_edit_news page
        self.assertTemplateUsed(response, 'events/auto_edit_news.html')

        # Check that News was created with is_published=False
        news = News.objects.filter(event=new_event).first()
        self.assertIsNotNone(news)
        self.assertFalse(news.is_published)
        self.assertIn("Super Event", news.title)

    def test_co_manager_can_create_event(self):
        self.client.login(email='co@uni.ac.uk', password='copass')
        data = {
            'name': 'Co-Managed Event',
            'description': 'desc...',
            'date': '2025-06-10T12:00',
            'event_type': 'academic',
            'keyword': 'study',
            'location': 'Library',
            'capacity': '50',
            'member_only': True,
            'fee': '0.00',
            'is_free': True,
            'society': [str(self.society.id)]
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Event.objects.filter(name='Co-Managed Event').exists())

    def test_editor_can_create_event(self):
        self.client.login(email='editor@uni.ac.uk', password='editpass')
        data = {
            'name': 'Editor Created Event',
            'description': 'desc...',
            'date': '2025-07-12T09:30',
            'event_type': 'arts',
            'keyword': 'painting',
            'location': 'Art Hall',
            'capacity': '30',
            'member_only': False,
            'fee': '0.00',
            'is_free': True,
            'society': [str(self.society.id)]
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Event.objects.filter(name='Editor Created Event').exists())

    def test_normal_user_cannot_create_event(self):
        self.client.login(email='normal@uni.ac.uk', password='normalpass')
        data = {
            'name': 'Secret Event',
            'description': 'No permission',
            'date': '2025-05-02T14:00',
            'event_type': 'social',
            'keyword': 'secret',
            'location': 'Gym',
            'capacity': '20',
            'member_only': False,
            'fee': '0.00',
            'is_free': True,
            'society': [str(self.society.id)]
        }
        response = self.client.post(self.url, data, follow=True)
        # Should redirect or show error, but not create event
        self.assertFalse(Event.objects.filter(name='Secret Event').exists())
        self.assertContains(response, "do not have permission", status_code=200)

    def test_must_login(self):
        # Anonymous user
        data = {
            'name': 'Anon Event',
            'description': 'desc...',
            'date': '2025-05-12T10:00',
            'event_type': 'cultural',
            'keyword': 'culture',
            'location': 'Main Quad',
            'capacity': '200',
            'member_only': False,
            'fee': '0.00',
            'is_free': True,
            'society': [str(self.society.id)]
        }
        response = self.client.post(self.url, data)
        # Should redirect to login
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(Event.objects.filter(name='Anon Event').exists())


class AutoEditNewsViewTests(TestCase):
    """
    Tests for auto_edit_news that displays a modelformset of the News items 
    linked to a newly created event.
    - Must be logged in
    - The newly created news must be is_published=False initially
    - On POST, it sets is_published=True
    """

    def setUp(self):
        self.client = Client()

        # Create user, event, news
        self.user_manager = User.objects.create_user(
            email='manager@uni.ac.uk',
            password='mgrpass'
        )

        # We'll create a society for context, though we only need event->news
        self.society = Society.objects.create(
            name='EventSociety',
            manager=self.user_manager,
            status='approved',
            society_type='academic'
        )
        Membership.objects.create(
            society=self.society,
            user=self.user_manager,
            role=MembershipRole.MANAGER,
            status=MembershipStatus.APPROVED
        )

        self.event = Event.objects.create(
            name='TestEvent',
            description='Testing auto-edit news',
            date=timezone.now(),
            event_type='sports',
            keyword='sport',
            location='Arena',
            capacity=100,
            member_only=False,
            fee=0,
            is_free=True,
        )
        # Suppose your signal or your code creates 1 or more News entries:
        self.news1 = News.objects.create(
            title='Auto News 1',
            content='Auto content 1',
            society=self.society,
            event=self.event,
            is_published=False
        )
        # Suppose there's a second news item if multiple societies host the event
        self.news2 = News.objects.create(
            title='Auto News 2',
            content='Auto content 2',
            society=self.society,
            event=self.event,
            is_published=False
        )

        self.url = reverse('auto_edit_news', args=[self.event.id])

    def test_must_login(self):
        # If user is not logged in => redirect to login
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)

    def test_shows_unpublished_news_formset(self):
        # Manager logs in
        self.client.login(email='manager@uni.ac.uk', password='mgrpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Auto News 1')
        self.assertContains(response, 'Auto News 2')

        # The formset includes 2 forms, one for each news item
        self.assertContains(response, 'id_form-0-title')
        self.assertContains(response, 'id_form-1-title')

    def test_publish_news(self):
        self.client.login(email='manager@uni.ac.uk', password='mgrpass')
        get_resp = self.client.get(self.url)
        self.assertEqual(get_resp.status_code, 200)

        post_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',

            'form-0-id': str(self.news1.id),
            'form-0-title': 'Updated Title 1',
            'form-0-content': 'Updated Content 1',
            'form-0_society': str(self.society.name),  # or ID if your form uses a ModelChoice
            # The default NewsForm might have 'society' or not, depends on your fields
            'form-0_date_posted': '2025-01-01T12:00',

            'form-1-id': str(self.news2.id),
            'form-1-title': 'Updated Title 2',
            'form-1-content': 'Updated Content 2',
            'form-1_society': str(self.society.name),
            'form-1_date_posted': '2025-01-02T08:00',
        }
        post_resp = self.client.post(self.url, post_data, follow=True)
        self.assertEqual(post_resp.status_code, 200)
        self.assertContains(post_resp, "News updated and published!")

        # Check the news is now published
        self.news1.refresh_from_db()
        self.news2.refresh_from_db()
        self.assertTrue(self.news1.is_published)
        self.assertTrue(self.news2.is_published)
        self.assertEqual(self.news1.title, 'Updated Title 1')
        self.assertEqual(self.news2.title, 'Updated Title 2')