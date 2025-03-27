from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.widgets.models import Widget
from apps.societies.models import Society
from config.constants import WIDGET_TYPES

User = get_user_model()

class WidgetModelTests(TestCase):
    """Tests for the Widget model"""

    def setUp(self):
        # Create a manager for the society.
        self.manager = User.objects.create_user(
            email="manager@example.com",
            first_name="Manager",
            last_name="User",
            preferred_name="Manager", 
            password="password123"
        )
        # Create a test society. 
        self.society = Society.objects.create(
            name="Test Society",
            description="A society for testing widgets.",
            society_type="Test",
            manager=self.manager,
            members_count=0,
        )
        # Create two widget instances with different types and positions.
        self.widget1 = Widget.objects.create(
            society=self.society,
            widget_type="announcements",  
            position=1,
            custom_html="<p>Announcement Widget</p>",
            data={"sample": "data"}
        )
        self.widget2 = Widget.objects.create(
            society=self.society,
            widget_type="gallery",
            position=2,
            custom_html="",
            data={}
        )

    def test_widget_creation(self):
        """Test that a widget is created with correct field values."""
        widget = self.widget1
        self.assertEqual(widget.society, self.society)
        self.assertEqual(widget.widget_type, "announcements")
        self.assertEqual(widget.position, 1)
        self.assertEqual(widget.custom_html, "<p>Announcement Widget</p>")
        self.assertEqual(widget.data, {"sample": "data"})

    def test_widget_str_method(self):
        """Test the string representation of the widget model."""
        widget = self.widget1
        expected_str = f"{widget.get_widget_type_display()} for {self.society.name}"
        self.assertEqual(str(widget), expected_str)

    def test_widget_ordering(self):
        """Test that widgets are ordered by the 'position' field."""
        widget0 = Widget.objects.create(
            society=self.society,
            widget_type="contacts",
            position=0,
            custom_html="",
            data={}
        )
        widgets = list(Widget.objects.filter(society=self.society))
        self.assertEqual(widgets[0], widget0)
        self.assertEqual(widgets[1], self.widget1)
        self.assertEqual(widgets[2], self.widget2)
