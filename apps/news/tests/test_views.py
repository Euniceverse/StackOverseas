from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from apps.news.models import News
from apps.societies.models import Society

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
        self.assertTemplateUsed(response, "news-panel.html")  
        self.assertContains(response, "Published News 1") 
        self.assertContains(response, "Published News 2") 
        self.assertNotContains(response, "Unpublished News") 


User = get_user_model()


class NewsViewTests(TestCase):
    """Tests for the news creation view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="manager@example.ac.uk",
            first_name="Test",
            last_name="Manager",
            preferred_name="Manager",
            password="password123"
        )

        self.society = Society.objects.create(
            name="Tech Society",
            description="A society for tech enthusiasts.",
            society_type="Technology",
            manager=self.user,
            status="approved" 
        )

        self.news_url = reverse("create_news")
        
    def test_redirect_if_not_logged_in(self):
        """Test that an unauthenticated user is redirected."""
        response = self.client.get(self.news_url)
        self.assertEqual(response.status_code, 302) 

    def test_access_form_as_manager(self):
        """Test that a society manager can access the news form."""
        self.client.login(email="manager@example.ac.uk", password="password123")
        response = self.client.get(self.news_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create a News Article")

    def test_create_news_post_success(self):
        """Test that a society manager can successfully submit news."""
        self.client.login(email="manager@example.ac.uk", password="password123")

        response = self.client.post(self.news_url, {
            "title": "New Tech Event",
            "content": "Join us for an exciting event!",
            "society": str(self.society.id), 
            "date_posted": now().strftime("%Y-%m-%dT%H:%M"), 
            "post": "1"
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(News.objects.filter(title="New Tech Event").exists())

    def test_unauthorized_news_submission(self):
        """Test that a user cannot submit news for a society they don't manage."""
        other_user = User.objects.create_user(
            email="unauthorized@example.ac.uk",
            first_name="Unauth",
            last_name="User",
            preferred_name="User",
            password="password123"
        )

        self.client.login(email="unauthorized@example.ac.uk", password="password123")

        response = self.client.post(self.news_url, {
            "title": "Unauthorized News",
            "content": "This should not be allowed.",
            "society": self.society.id,
            "date_posted": now(),
        })

        self.assertEqual(response.status_code, 302) 
        self.assertFalse(News.objects.filter(title="Unauthorized News").exists())
