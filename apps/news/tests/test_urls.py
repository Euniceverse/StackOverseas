from django.urls import reverse, resolve
from django.test import SimpleTestCase
from apps.news import views

class NewsUrlsTest(SimpleTestCase):
    def test_newspage_url(self):
        url = reverse('newspage')
        self.assertEqual(resolve(url).func, views.newspage)

    def test_news_list_url(self):
        url = reverse('news_list')
        self.assertEqual(resolve(url).func, views.news_list)

    def test_news_panel_url(self):
        url = reverse('news_panel')
        self.assertEqual(resolve(url).func, views.news_list)

    def test_create_news_url(self):
        url = reverse('create_news')
        self.assertEqual(resolve(url).func, views.create_news)

    def test_edit_news_url(self):
        url = reverse('edit_news', kwargs={'news_id': 1})
        self.assertEqual(resolve(url).func, views.edit_news)

    def test_news_detail_url(self):
        url = reverse('news_detail', kwargs={'news_id': 1})
        self.assertEqual(resolve(url).func, views.news_detail)