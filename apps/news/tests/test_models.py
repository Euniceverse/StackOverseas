from django.test import TestCase
from django.utils import timezone
from apps.news.models import News

class NewsModelTests(TestCase):
    """Tests for the News model"""

    def setUp(self):
        """Set up test news objects"""
        self.news1 = News.objects.create(
            title="Published News",
            content="This is a test news article.",
            society="Tech Society",
            date_posted=timezone.now(),
            is_published=True
        )

        self.news2 = News.objects.create(
            title="Unpublished News",
            content="This news should not be publicly visible.",
            society="Hidden Society",
            date_posted=timezone.now(),
            is_published=False
        )

    def test_news_creation(self):
        """Test that news objects are created correctly"""
        self.assertEqual(self.news1.title, "Published News")
        self.assertEqual(self.news1.content, "This is a test news article.")
        self.assertTrue(self.news1.is_published)

    def test_published_news_queryset(self):
        """Test that only published news appears in published queries"""
        published_news = News.objects.filter(is_published=True)
        self.assertEqual(published_news.count(), 1)
        self.assertEqual(published_news.first(), self.news1)

    def test_unpublished_news_not_in_queryset(self):
        """Test that unpublished news does not appear in published queries"""
        published_news_titles = list(News.objects.filter(is_published=True).values_list("title", flat=True))
        self.assertNotIn("Unpublished News", published_news_titles)

    def test_news_str_method(self):
        """Test the string representation of news model"""
        self.assertEqual(str(self.news1), "Published News")

