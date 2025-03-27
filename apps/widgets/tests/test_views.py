import json
from django.test import TestCase, Client
from django.urls import reverse
from apps.widgets.models import Widget
from apps.societies.models import Society, Membership, MembershipRole, MembershipStatus
from apps.users.models import CustomUser

class WidgetViewsTests(TestCase):
    def setUp(self):
        # Create test users: a manager and a regular (co-manager) user.
        self.manager = CustomUser.objects.create_user(
            email="manager@example.com",
            first_name="Manager",
            last_name="User",
            preferred_name="Manager",
            password="password123"
        )
        self.co_manager = CustomUser.objects.create_user(
            email="comanager@example.com",
            first_name="CoManager",
            last_name="User",
            preferred_name="CoManager",
            password="password123"
        )
        # Create a test society
        self.society = Society.objects.create(
            name="Test Society",
            description="A society for testing widgets.",
            society_type="Test",
            manager=self.manager,
            members_count=1,
        )
        # Create a membership for the co-manager user
        self.membership = Membership.objects.create(
            society=self.society,
            user=self.co_manager,
            role=MembershipRole.CO_MANAGER,
            status=MembershipStatus.APPROVED
        )
        # Create two widgets
        self.widget1 = Widget.objects.create(
            society=self.society,
            widget_type="announcements",
            position=1,
            custom_html="<p>Announcement Widget</p>",
            data={"sample": "data1"}
        )
        self.widget2 = Widget.objects.create(
            society=self.society,
            widget_type="gallery",
            position=2,
            custom_html="",
            data={}
        )
        self.client = Client()

    def test_update_widget_order_as_manager(self):
        """Test updating widget order via JSON POST as society manager."""
        self.client.login(email="manager@example.com", password="password123")
        update_url = reverse("update_widget_order", kwargs={"society_id": self.society.id})
        new_order = [self.widget2.id, self.widget1.id]
        response = self.client.post(update_url, data=json.dumps({"widget_order": new_order}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.widget1.refresh_from_db()
        self.widget2.refresh_from_db()
        self.assertEqual(self.widget2.position, 0)
        self.assertEqual(self.widget1.position, 1)

    def test_remove_widget_as_manager(self):
        """Test removing a widget as society manager returns a redirect to manage display."""
        self.client.login(email="manager@example.com", password="password123")
        remove_url = reverse("remove_widget", kwargs={"society_id": self.society.id, "widget_id": self.widget1.id})
        response = self.client.post(remove_url)
        self.assertRedirects(response, reverse("manage_display", kwargs={"society_id": self.society.id}))
        with self.assertRaises(Widget.DoesNotExist):
            Widget.objects.get(id=self.widget1.id)

    def test_remove_widget_as_co_manager(self):
        """Test that a co-manager (allowed role) can remove a widget."""
        self.client.login(email="comanager@example.com", password="password123")
        remove_url = reverse("remove_widget", kwargs={"society_id": self.society.id, "widget_id": self.widget2.id})
        response = self.client.post(remove_url)
        self.assertRedirects(response, reverse("manage_display", kwargs={"society_id": self.society.id}))
        with self.assertRaises(Widget.DoesNotExist):
            Widget.objects.get(id=self.widget2.id)

    def test_edit_contact_widget_get(self):
        """Test GET request on edit_contact_widget returns status 200 and contains expected text."""
        contact_widget = Widget.objects.create(
            society=self.society,
            widget_type="contacts",
            position=3,
            custom_html="",
            data={"phone": "1234567890", "email": "contact@example.com"}
        )
        self.client.login(email="manager@example.com", password="password123")
        url = reverse("edit_widget", kwargs={"society_id": self.society.id, "widget_id": contact_widget.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter phone number") 

    def test_edit_featured_members_widget_get(self):
        """Test that GET request to edit_featured_members_widget returns status 200 and contains expected form elements."""
        featured_data = {
            'featured_members': [
                {'member': 'Alice', 'role': 'President', 'picture': 'path/to/alice.png'}
            ]
        }
        featured_widget = Widget.objects.create(
            society=self.society,
            widget_type="featured",
            position=4,
            custom_html="",
            data=featured_data
        )
        self.client.login(email="manager@example.com", password="password123")
        url = reverse("edit_widget", kwargs={"society_id": self.society.id, "widget_id": featured_widget.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Featured Members for")
        self.assertContains(response, "Select a member")


    def test_edit_announcements_widget_get(self):
        """Test GET request for announcements widget edit view."""
        announcements_data = {
            'announcements': [
                {'title': 'Test Announcement', 'message': 'Details here', 'date': '2025-03-27'}
            ]
        }
        announcement_widget = Widget.objects.create(
            society=self.society,
            widget_type="announcements",
            position=5,
            custom_html="",
            data=announcements_data
        )
        self.client.login(email="manager@example.com", password="password123")
        url = reverse("edit_widget", kwargs={"society_id": self.society.id, "widget_id": announcement_widget.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Announcement")

    def test_edit_leaderboard_widget_get(self):
        """Test GET request for leaderboard widget edit view."""
        leaderboard_data = {
            'points': {"1": 10, "2": 5},
            'display_points': True,
            'display_count': 3,
        }
        leaderboard_widget = Widget.objects.create(
            society=self.society,
            widget_type="leaderboard",
            position=6,
            custom_html="",
            data=leaderboard_data
        )
        self.client.login(email="manager@example.com", password="password123")
        url = reverse("edit_widget", kwargs={"society_id": self.society.id, "widget_id": leaderboard_widget.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Number of Top Entries to Display")
