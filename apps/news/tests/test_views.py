from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from apps.news.models import News, F
from apps.societies.models import Society
from apps.news.forms import NewsForm
from django.shortcuts import reverse

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
    
class EditNewsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a manager user
        self.user = User.objects.create_user(
            email="manager2@example.ac.uk",
            first_name="Edit2",
            last_name="Manager2",
            preferred_name="Manager2",
            password="password123"
        )
        # Create a society
        self.society = Society.objects.create(
            name="EditTest Society",
            description="desc",
            society_type="sports",
            manager=self.user,
            status="approved"
        )
        # Create a News item
        self.news_item = News.objects.create(
            title="Editable News",
            content="News content",
            society=self.society,
            is_published=True
        )
        self.edit_url = reverse("edit_news", args=[self.news_item.id])

    def test_edit_news_requires_login(self):
        response = self.client.get(self.edit_url)
        # Should redirect to login
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f'/accounts/login/?next={self.edit_url}')

    def test_edit_news_get_as_manager(self):
        self.client.login(email="manager2@example.ac.uk", password="password123")
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_news.html")
        self.assertContains(response, "Editable News")

    def test_edit_news_post_valid(self):
        self.client.login(email="manager2@example.ac.uk", password="password123")
        # Provide updated data
        post_data = {
            "title": "Updated Title",
            "content": "Updated Content",
            "society": str(self.society.id),
            "date_posted": self.news_item.date_posted.strftime("%Y-%m-%dT%H:%M"),
        }
        response = self.client.post(self.edit_url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Check that it updated
        self.news_item.refresh_from_db()
        self.assertEqual(self.news_item.title, "Updated Title")
        self.assertEqual(self.news_item.content, "Updated Content")

    def test_edit_news_post_invalid(self):
        """If we post missing fields, it should show form errors."""
        self.client.login(email="manager2@example.ac.uk", password="password123")
        post_data = {
            "title": "",  # invalid
            "content": "",
            "society": str(self.society.id),
            "date_posted": self.news_item.date_posted.strftime("%Y-%m-%dT%H:%M"),
        }
        response = self.client.post(self.edit_url, post_data)
        # The form is invalid => status_code=200 but with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")


class NewsDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="viewer@example.ac.uk",
            first_name="View",
            last_name="User",
            preferred_name="Viewer",
            password="password123"
        )
        # Society for completeness
        self.society = Society.objects.create(
            name="Detail Society",
            manager=self.user,
            society_type="sports",
            status="approved"
        )
        # A News item with initial views=5
        self.news_item = News.objects.create(
            title="Detail News",
            content="Some details",
            society=self.society,
            views=5,
            is_published=True
        )
        self.detail_url = reverse("news_detail", args=[self.news_item.id])

    def test_news_detail_increments_views(self):
        """Check that visiting news_detail increments views."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news_detail.html")

        # Refresh from DB => views should be 6
        updated = News.objects.get(id=self.news_item.id)
        self.assertEqual(updated.views, 6)
        self.assertContains(response, "Detail News")