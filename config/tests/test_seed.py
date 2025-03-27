import os
import random
import sys
import torch
from types import ModuleType

dummy_constants = ModuleType("constants")
dummy_constants.UNI_CHOICES = {"TestCity": ["test_uni"]}
dummy_constants.SOCIETY_TYPE_CHOICES = [("alpha", "Alpha"), ("beta", "Beta")]
dummy_constants.SOCIETY_STATUS_CHOICES = [("approved", "Approved"), ("pending", "Pending")]
dummy_constants.EVENT_TYPE_CHOICES = [("music", "Music"), ("education", "Education")]
sys.modules["constants"] = dummy_constants

dummy_ai_seed = ModuleType("ai_seed")
dummy_ai_seed.generate_society_description = lambda name, society_type: "Dummy description"
dummy_ai_seed.generate_society_name = lambda society_type, existing_names: "Dummy Society Name"
dummy_ai_seed.generate_event_location = lambda city: "Dummy Location"
sys.modules["ai_seed"] = dummy_ai_seed

from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from config import seed  
from apps.societies.models import Society, Membership
from apps.events.models import Event, EventRegistration
from apps.news.models import News


class RandomLocationTest(TestCase):
    def test_random_location_not_online(self):
        original_choice = random.choice
        def fake_choice(seq):
            if "Online" in seq:
                seq = [item for item in seq if item != "Online"]
                return seq[0]
            return original_choice(seq)
        random.choice = fake_choice
        location = seed.random_location()
        self.assertNotEqual(location, "Online")
        random.choice = original_choice

class CreateSuperuserTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.superuser_email = "admin@example.ac.uk"
        self.User.objects.filter(email=self.superuser_email).delete()

    def test_create_superuser_creates_if_not_exists(self):
        seed.create_superuser()
        self.assertTrue(self.User.objects.filter(email=self.superuser_email).exists())

    def test_create_superuser_skips_if_exists(self):
        self.User.objects.create_superuser(
            email=self.superuser_email,
            first_name="Admin",
            last_name="User",
            preferred_name="Admin",
            password="password123"
        )
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output
        seed.create_superuser()
        sys.stdout = sys.__stdout__
        self.assertIn("Superuser already exists", captured_output.getvalue())

class GenerateUniqueEmailTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.User.objects.all().delete()

    def test_generate_unique_email(self):
        email1 = seed.generate_unique_email("John", "Doe")
        self.assertIn("john.doe", email1)
        self.User.objects.create_user(
            email=email1,
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="password"
        )
        email2 = seed.generate_unique_email("John", "Doe")
        self.assertNotEqual(email1, email2)

class CreateDummyUsersTest(TestCase):
    def test_create_dummy_users_returns_list(self):
        users = seed.create_dummy_users(10)
        self.assertEqual(len(users), 10)
        emails = [user.email for user in users]
        self.assertEqual(len(emails), len(set(emails)))

class GetLocationFromEmailTest(TestCase):
    def test_get_location_from_email_found(self):
        original_uni = seed.constants.UNI_CHOICES.copy()
        seed.constants.UNI_CHOICES = {'CityX': ['uni1', 'uni2'], 'CityY': ['uni3']}
        email = "someone@uni1.ac.uk"
        self.assertEqual(seed.get_location_from_email(email), "CityX")
        seed.constants.UNI_CHOICES = original_uni

    def test_get_location_from_email_not_found(self):
        original_uni = seed.constants.UNI_CHOICES.copy()
        seed.constants.UNI_CHOICES = {'CityX': ['uni1', 'uni2']}
        email = "someone@unknown.ac.uk"
        self.assertEqual(seed.get_location_from_email(email), "Unknown")
        seed.constants.UNI_CHOICES = original_uni

class CreateDummySocietiesTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.users = seed.create_dummy_users(5)

    def test_create_dummy_societies(self):
        from unittest.mock import patch
        with patch('config.seed.generate_society_name', side_effect=["Test Society", "Test Society 1", "Test Society 2"]), \
             patch('config.seed.generate_society_description', return_value="A test society description"):
            societies = seed.create_dummy_societies(self.users, n=3)
        self.assertEqual(len(societies), 3)
        expected_names = {"Test Society", "Test Society 1", "Test Society 2"}
        for society in societies:
            self.assertIn(society.name, expected_names)
            self.assertEqual(society.description, "A test society description")
            self.assertTrue(society.location != "")

class RandomLocationCordTest(TestCase):
    def test_random_location_cord_in_range(self):
        lat, lon = seed.random_location_cord()
        self.assertGreaterEqual(lat, seed.LAT_MIN)
        self.assertLessEqual(lat, seed.LAT_MAX)
        self.assertGreaterEqual(lon, seed.LON_MIN)
        self.assertLessEqual(lon, seed.LON_MAX)

class CreateDummyEventsTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.manager = self.User.objects.create_user(
            email="event@test.com", password="test",
            first_name="Event", last_name="Manager", preferred_name="EManager"
        )
        self.society = Society.objects.create(name="TestSociety", status="approved", manager=self.manager)

    def test_create_dummy_events(self):
        from unittest.mock import patch
        with patch('config.seed.generate_event_location', return_value="Test Location"):
            events = seed.create_dummy_events([self.society], n=5)
        self.assertEqual(len(events), 5)
        for event in events:
            self.assertEqual(event.location, "Test Location")
            self.assertTrue(hasattr(event, 'date'))
            self.assertTrue(event.society.exists())

class CreateDummyEventRegistrationsTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email="reg@test.com", password="test",
            first_name="Reg", last_name="User", preferred_name="Reg"
        )
        self.manager = self.User.objects.create_user(
            email="event@test.com", password="test",
            first_name="Event", last_name="Manager", preferred_name="EManager"
        )
        self.society = Society.objects.create(name="TestSociety", status="approved", manager=self.manager)
        self.event = Event.objects.create(
            name="Concert", event_type="music", description="awesome music", fee=10, date=timezone.now().date()
        )
        self.event.society.add(self.society)

    def test_create_dummy_event_registrations(self):
        initial = EventRegistration.objects.count()
        seed.create_dummy_event_registrations([self.user], [self.event], n=3)
        self.assertEqual(EventRegistration.objects.count(), initial + 3)

class CreateDummyMembershipsTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.users = seed.create_dummy_users(10)
        self.manager = self.users[0]
        self.society = Society.objects.create(name="TestSociety", status="approved", manager=self.manager)

    def test_create_dummy_memberships(self):
        initial = Membership.objects.count()
        seed.create_dummy_memberships(self.users, [self.society])
        self.assertGreater(Membership.objects.count(), initial)

class CreateFakeNewsTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.manager = self.User.objects.create_user(
            email="news@test.com", password="test",
            first_name="News", last_name="Manager", preferred_name="NM"
        )
        self.society = Society.objects.create(name="NewsSociety", status="approved", manager=self.manager)
        News.objects.create(title="Old News", is_published=True, date_posted=timezone.now(), society=self.society)

    def test_create_fake_news(self):
        seed.create_fake_news()
        news_count = News.objects.count()
        self.assertEqual(news_count, 20)
        for news in News.objects.all():
            self.assertTrue(news.is_published)
            self.assertEqual(news.society.status, "approved")