import json
from django.test import TestCase, RequestFactory
from django.http import HttpRequest
from unittest.mock import patch, MagicMock
from config.views import home, ai_search
from collections import namedtuple
from django.urls import reverse

class HomeViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password",
            first_name="Test",
            last_name="User",
            preferred_name="Test"
        )
        self.client.force_login(self.user)

    @patch('django.urls.reverse', side_effect=lambda view, *args, **kwargs: '/dummy_society/')
    @patch('config.views.top_societies')
    @patch('config.views.get_recent_news')
    def test_home_view(self, mock_get_recent_news, mock_top_societies, mock_reverse):
        fake_news = ['news1', 'news2']
        DummySoc = namedtuple("DummySoc", ["id", "name"])
        dummy_soc = DummySoc(id=1, name="Soc1")
        
        fake_top_societies = {
            'top_societies_per_type': {'A': [dummy_soc]},
            'top_overall_societies': [dummy_soc]
        }
        mock_get_recent_news.return_value = fake_news
        mock_top_societies.return_value = fake_top_societies

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('news_list', response.context)
        self.assertEqual(response.context['news_list'], fake_news)
        self.assertIn('top_societies_per_type', response.context)
        self.assertEqual(response.context['top_societies_per_type'],
                         fake_top_societies['top_societies_per_type'])
        self.assertIn('top_overall_societies', response.context)
        self.assertEqual(response.context['top_overall_societies'],
                         fake_top_societies['top_overall_societies'])
        self.assertIn('user', response.context)
        self.assertEqual(response.context['user'].pk, self.user.pk)

class AISearchViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('config.views.search_societies')
    def test_ai_search_societies_default(self, mock_search_societies):
        fake_results = ['soc1', 'soc2']
        fake_suggestion = 'try another term'
        mock_search_societies.return_value = (fake_results, fake_suggestion)

        response = self.client.get(reverse('ai_search') + '?q=example')
        self.assertEqual(response.status_code, 200)
        self.assertIn('societies', response.context)
        self.assertEqual(response.context['societies'], fake_results)
        self.assertIn('suggestion', response.context)
        self.assertEqual(response.context['suggestion'], fake_suggestion)
        self.assertIn('page', response.context)
        self.assertEqual(response.context['page'], 'Search')

    @patch('apps.events.models.Event')
    def test_ai_search_events(self, mock_event):
        fake_queryset = MagicMock()
        fake_queryset.filter.return_value = ['event1', 'event2']
        mock_event.objects.filter.return_value = fake_queryset.filter.return_value

        response = self.client.get(reverse('ai_search') + '?q=concert&search_type=events')
        self.assertEqual(response.status_code, 200)
        self.assertIn('events', response.context)
        self.assertEqual(response.context['events'], ['event1', 'event2'])
        self.assertIn('page', response.context)
        self.assertEqual(response.context['page'], 'Search Results')