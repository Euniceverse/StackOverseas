from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from apps.news.models import News
from apps.users.models import CustomUser
from apps.societies.models import Society, Membership, MembershipRole, MembershipStatus
from apps.news.forms import NewsForm

User = get_user_model()

class NewsViewTests(TestCase):
    """Testing for the News View"""

    def setUp(self):
        """Set up test data"""
        # create manager instance
        self.manager = CustomUser.objects.create_user(
            email="manager@ac.uk",
            first_name="Manager",
            last_name="User",
            preferred_name="Manager",
            password="password123"
        )
        
        # create society instances
        self.society1 = Society.objects.create(
            name="Tech Society",
            description="A society for tech enthusiasts",
            society_type="Technology",
            manager=self.manager,
            status="approved"
        )
        
        self.society2 = Society.objects.create(
            name="Science Society",
            description="A society for science enthusiasts",
            society_type="Science",
            manager=self.manager,
            status="approved"
        )
        
        self.society3 = Society.objects.create(
            name="Hidden Society",
            description="A hidden society for testing",
            society_type="Hidden",
            manager=self.manager,
            status="approved"
        )
        
        # create news instances
        self.news1 = News.objects.create(
            title="Published News 1",
            content="Content for news 1",
            society=self.society1,
            date_posted=timezone.now(),
            is_published=True
        )
        self.news2 = News.objects.create(
            title="Published News 2",
            content="Content for news 2",
            society=self.society2,
            date_posted=timezone.now(),
            is_published=True
        )
        self.news3 = News.objects.create(
            title="Unpublished News",
            content="This news should not appear",
            society=self.society3,
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
        

class NewsViewTests(TestCase):
    """Tests for the news creation view."""
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="manager1@example.ac.uk",
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
        
        Membership.objects.create(
            society=self.society,
            user=self.user,
            role=MembershipRole.MANAGER,
            status=MembershipStatus.APPROVED
        )

        self.news_url = reverse("create_news_for_society", args=[self.society.id])
        
    def test_redirect_if_not_logged_in(self):
        """Test that an unauthenticated user is redirected."""
        response = self.client.get(self.news_url)
        self.assertEqual(response.status_code, 302) 

    def test_access_form_as_manager(self):
        """Test that a society manager can access the news form."""
        self.client.login(email="manager1@example.ac.uk", password="password123")
        response = self.client.get(self.news_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create News")

    def test_create_news_post_success(self):
        """Test that a society manager can successfully submit news."""
        self.client.login(email="manager1@example.ac.uk", password="password123")

        response = self.client.post(self.news_url, {
            "title": "New Tech Event",
            "content": "Join us for an exciting event!",
            "date_posted": now().strftime("%Y-%m-%dT%H:%M"), 
            "post": "Submit",
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
    """Test for EditNewsView."""
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
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f'{reverse("log_in")}?next={self.edit_url}')

    def test_edit_news_get_as_manager(self):
        self.client.login(email="manager2@example.ac.uk", password="password123")
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_news.html")
        self.assertContains(response, "Editable News")

    def test_edit_news_post_valid(self):
        self.client.login(email="manager2@example.ac.uk", password="password123")
        post_data = {
            "title": "Updated Title",
            "content": "Updated Content",
            "society": self.society.id,
            "date_posted": self.news_item.date_posted.strftime("%Y-%m-%dT%H:%M"),
            "is_published": self.news_item.is_published,
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
            "society": self.society.id,
            "date_posted": self.news_item.date_posted.strftime("%Y-%m-%dT%H:%M"),
        }
        response = self.client.post(self.edit_url, post_data)
        # The form is invalid => status_code=200 but with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")


class NewsDetailViewTests(TestCase):
    """Test for NewsDetail view."""
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

# ... existing imports and test classes in test_views.py remain unchanged ...

class NewsPageSortingTests(TestCase):
    """Additional tests for the newspage view sorting and context variables."""
    def setUp(self):
        # Create a manager user
        self.manager = CustomUser.objects.create_user(
            email="manager@ac.uk",
            password="password123",
            first_name="Manager",
            last_name="User",
            preferred_name="Manager"
        )
        # Create societies (all approved)
        self.society = Society.objects.create(
            name="Tech Society",
            description="A society for tech enthusiasts",
            society_type="Technology",
            manager=self.manager,
            status="approved"
        )
        # Create several news items with distinct date_posted and views
        now_time = timezone.now()
        self.news1 = News.objects.create(
            title="News A",
            content="Content A",
            society=self.society,
            date_posted=now_time - timezone.timedelta(days=3),
            views=10,
            is_published=True
        )
        self.news2 = News.objects.create(
            title="News B",
            content="Content B",
            society=self.society,
            date_posted=now_time - timezone.timedelta(days=2),
            views=20,
            is_published=True
        )
        self.news3 = News.objects.create(
            title="News C",
            content="Content C",
            society=self.society,
            date_posted=now_time - timezone.timedelta(days=1),
            views=5,
            is_published=True
        )
        self.url = reverse("newspage")

    def test_default_sorting_newest(self):
        """Test that by default, news are sorted with newest first."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        news_list = list(response.context["news_list"])
        # Since "newest" is default, the first news item should be the one with the most recent date_posted.
        self.assertEqual(news_list[0].title, "News C")

        # Also, check that selected_sort is set to "newest" in context.
        self.assertEqual(response.context.get("selected_sort"), "newest")

    def test_sorting_oldest(self):
        """Test that sorting by 'oldest' returns news in ascending order of date_posted."""
        response = self.client.get(self.url + "?sort=oldest")
        self.assertEqual(response.status_code, 200)
        news_list = list(response.context["news_list"])
        # In ascending order, the oldest (news1) comes first.
        self.assertEqual(news_list[0].title, "News A")
        self.assertEqual(response.context.get("selected_sort"), "oldest")

    def test_sorting_popularity(self):
        """Test that sorting by 'popularity' returns news in descending order of views."""
        response = self.client.get(self.url + "?sort=popularity")
        self.assertEqual(response.status_code, 200)
        news_list = list(response.context["news_list"])
        # news2 has the highest views (20) so should come first.
        self.assertEqual(news_list[0].title, "News B")
        self.assertEqual(response.context.get("selected_sort"), "popularity")

    def test_context_includes_societies_and_choices(self):
        """Test that the context contains societies and SOCIETY_TYPE_CHOICES."""
        response = self.client.get(self.url)
        self.assertIn("societies", response.context)
        self.assertIn("SOCIETY_TYPE_CHOICES", response.context)        