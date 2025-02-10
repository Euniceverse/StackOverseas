from django.test import TestCase
from django.urls import reverse
from apps.news.models import News
from django.utils import timezone

class NewsViewTests(TestCase):
    """Testing for the News View"""

    def setUp(self):
        """Set up test data"""
        self.news1 = News.objects.create(
            title="Published News 1",
            content="Content for news 1",
            society="Tech Society",
            date_posted=timezone.now(),
            is_published=True
        )
        self.news2 = News.objects.create(
            title="Published News 2",
            content="Content for news 2",
            society="Science Society",
            date_posted=timezone.now(),
            is_published=True
        )
        self.news3 = News.objects.create(
            title="Unpublished News",
            content="This news should not appear",
            society="Hidden Society",
            date_posted=timezone.now(),
            is_published=False
        )

    def test_newspage_view(self):
        """Test that the newspage view loads correctly"""
        response = self.client.get(reverse("newspage"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news.html")

    def test_news_list_view(self):
        """Test that the news list view only shows published news"""
        response = self.client.get(reverse("news_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news.html")  
        self.assertContains(response, "Published News 1") 
        self.assertContains(response, "Published News 2") 
        self.assertNotContains(response, "Unpublished News") 