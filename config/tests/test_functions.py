import json
import torch
from collections import namedtuple
from django.test import TestCase
from django.utils.timezone import now, timedelta
from unittest.mock import patch, MagicMock
from config.functions import (
    correct_spelling, autocomplete, search_events, 
    search_societies, get_recent_news
)
from symspellpy import Verbosity
from apps.events.models import Event
from apps.societies.models import Society
from apps.news.models import News
from django.contrib.auth import get_user_model


class CorrectSpellingTest(TestCase):
    @patch('config.functions.sym_spell.lookup')
    def test_correct_spelling_found(self, mock_lookup):
        mock_lookup.return_value = [MagicMock(term="hello")]
        result = correct_spelling("helo")
        self.assertEqual(result, "hello")

    @patch('config.functions.sym_spell.lookup')
    def test_correct_spelling_not_found(self, mock_lookup):
        mock_lookup.return_value = []
        result = correct_spelling("helo")
        self.assertEqual(result, "helo")


class AutocompleteTest(TestCase):
    @patch('config.functions.requests.get')
    def test_autocomplete_found(self, mock_get):
        fake_json = [{"word": "world"}]
        mock_get.return_value.json.return_value = fake_json
        result = autocomplete("hello")
        self.assertEqual(result, "world")

    @patch('config.functions.requests.get')
    def test_autocomplete_not_found(self, mock_get):
        mock_get.return_value.json.return_value = []
        result = autocomplete("hello")
        self.assertEqual(result, "hello")


class GetRecentNewsTest(TestCase):
    def setUp(self):
        User = get_user_model()
        dummy_manager = User.objects.create_user(
            email="news_manager@example.com",
            password="test",
            first_name="News",
            last_name="Manager",
            preferred_name="NM"
        )
        dummy_society = Society.objects.create(name="Dummy Society", status="approved", manager=dummy_manager)
    
        News.objects.create(title="News1", is_published=True, date_posted=now(), society=dummy_society)
        News.objects.create(title="News2", is_published=True, date_posted=now()-timedelta(days=1), society=dummy_society)
        News.objects.create(title="News3", is_published=False, date_posted=now()-timedelta(days=2), society=dummy_society)

    def test_get_recent_news_default(self):
        recent = get_recent_news()
        self.assertTrue(len(recent) <= 5)
        for news in recent:
            self.assertTrue(news.is_published)
        dates = [news.date_posted for news in recent]
        self.assertEqual(dates, sorted(dates, reverse=True))


class SearchEventsTest(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        manager = User.objects.create_user(
            email="event@test.com", password="test",
            first_name="Event", last_name="Manager", preferred_name="EManager"
        )
        self.society = Society.objects.create(name="TestSociety", status="approved", manager=manager)
        self.event1 = Event.objects.create(
            name="Concert", 
            event_type="music", 
            description="awesome music",
            fee = 10,
            date=now().date()
        )
        self.event1.society.add(self.society)

        self.event2 = Event.objects.create(
            name="Festival", 
            event_type="music", 
            description="fun festival", 
            fee=20,
            date=now().date()
        )
        self.event2.society.add(self.society)

        self.event3 = Event.objects.create(
            name="Lecture", 
            event_type="education", 
            description="interesting lecture", 
            fee=0,
            date=now().date()
        )
        self.event3.society.add(self.society)

    @patch('config.functions.model.encode')
    @patch('config.functions.util.pytorch_cos_sim')
    def test_search_events_by_type_found(self, mock_cos_sim, mock_encode):
        mock_encode.side_effect = lambda x, **kwargs: x  
        mock_cos_sim.return_value = torch.tensor([1.0, 0.5])
        results, suggestion = search_events("concert")
        for event in results:
            self.assertEqual(event.event_type, "music")
        self.assertEqual(suggestion, "concert")

    @patch('config.functions.model.encode')
    @patch('config.functions.util.pytorch_cos_sim')
    def test_search_events_no_event_types(self, mock_cos_sim, mock_encode):
        Event.objects.all().delete()
        results, suggestion = search_events("concert")
        self.assertEqual(results, [])
        self.assertEqual(suggestion, "concert")

    def test_search_events_empty_query(self):
        results, suggestion = search_events("")
        self.assertEqual(results, [])
        self.assertIsNone(suggestion)


class SearchSocietiesTest(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.manager = User.objects.create_user(
            email="soc@test.com", password="test",
            first_name="Soc", last_name="Manager", preferred_name="SManager"
        )
        self.society1 = Society.objects.create(
            name="Alpha Society", status="approved", society_type="alpha",
            description="first society", manager=self.manager
        )
        self.society2 = Society.objects.create(
            name="Beta Society", status="approved", society_type="beta",
            description="second society", manager=self.manager
        )
        self.society3 = Society.objects.create(
            name="Gamma Society", status="approved", society_type="alpha",
            description="third society", manager=self.manager
        )

    @patch('config.functions.model.encode')
    @patch('config.functions.util.pytorch_cos_sim')
    def test_search_societies_found(self, mock_cos_sim, mock_encode):
        mock_encode.side_effect = lambda x, **kwargs: x  
        mock_cos_sim.return_value = torch.tensor([0.9, 0.5])
        results, suggestion = search_societies("alpha")
        for soc in results:
            self.assertEqual(soc.society_type.lower(), "alpha")
        self.assertEqual(suggestion, "alpha")

    @patch('config.functions.model.encode')
    @patch('config.functions.util.pytorch_cos_sim')
    def test_search_societies_no_types(self, mock_cos_sim, mock_encode):
        Society.objects.all().delete()
        results, suggestion = search_societies("alpha")
        self.assertEqual(results, [])
        self.assertEqual(suggestion, "alpha")

    def test_search_societies_empty_query(self):
        results, suggestion = search_societies("")
        self.assertEqual(results, [])
        self.assertIsNone(suggestion)