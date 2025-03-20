from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from apps.news.forms import NewsForm
from apps.societies.models import Society

User = get_user_model()

class NewsFormTests(TestCase):
    """Tests for the NewsForm."""

    def setUp(self):
        """Set up test data."""
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
            manager=self.user
        )
        
        self.other_user = User.objects.create_user(
            email="other_manager@example.ac.uk",
            first_name="Other",
            last_name="Manager",
            preferred_name="OtherManager",
            password="password123"
        )
        
    def test_news_form_valid_data(self):
        """Test NewsForm with valid data."""
        form = NewsForm(
            data={
                "title": "New Event Announcement",
                "content": "Join us for a great event!",
                "society": self.society.id,
                "date_posted": now(),
            },
            user=self.user  
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_news_form_invalid_data(self):
        """Test NewsForm with missing fields."""
        form = NewsForm(
            data={},
            user=self.user
        )
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("content", form.errors)

    def test_news_form_filters_societies(self):
        """Test that NewsForm only allows societies managed by the user."""
        other_society = Society.objects.create(
            name="Other Society",
            description="Not managed by this user.",
            society_type="General",
            manager=self.other_user
        )

        form = NewsForm(user=self.user)
        self.assertIn(self.society, form.fields["society"].queryset)
        self.assertNotIn(other_society, form.fields["society"].queryset)