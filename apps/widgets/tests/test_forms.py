from django.test import TestCase
from apps.widgets.forms import (
    ContactWidgetForm,
    FeaturedMemberForm,
    AnnouncementForm,
    LeaderboardMembershipForm,
    LeaderboardSettingsForm,
)

class ContactWidgetFormTests(TestCase):
    """Tests for the ContactWidgetForm"""

    def test_empty_form_is_valid(self):
        """An empty contact widget form should be valid as all fields are optional."""
        form = ContactWidgetForm(data={})
        self.assertTrue(form.is_valid())

    def test_form_field_widget_attrs(self):
        """Each field should have the 'form-control' CSS class set."""
        form = ContactWidgetForm()
        for field_name, field in form.fields.items():
            self.assertIn(
                'form-control',
                field.widget.attrs.get('class', ''),
                msg=f"Field '{field_name}' is missing 'form-control' class."
            )

class FeaturedMemberFormTests(TestCase):
    """Tests for the FeaturedMemberForm"""

    def test_member_choices_initialization(self):
        """Test that the member dropdown is built correctly with given choices."""
        choices = ['Alice', 'Bob']
        form = FeaturedMemberForm(members_choices=choices)
        expected_choices = [("", "Select a member")] + [(name, name) for name in choices]
        self.assertEqual(form.fields['member'].choices, expected_choices)

    def test_required_fields_validation(self):
        """Test that required fields trigger validation errors when missing."""
        form = FeaturedMemberForm(data={}, members_choices=['Alice'])
        self.assertFalse(form.is_valid())
        self.assertIn('member', form.errors)
        self.assertIn('role', form.errors)

class AnnouncementFormTests(TestCase):
    """Tests for the AnnouncementForm"""

    def test_valid_announcement_form(self):
        """Test that a valid announcement form is valid and cleans data as expected."""
        data = {
            'title': 'Test Announcement',
            'message': 'This is a test announcement message.',
            'date': '2025-03-27'
        }
        form = AnnouncementForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'], 'Test Announcement')
        self.assertEqual(form.cleaned_data['message'], 'This is a test announcement message.')
        self.assertIsNotNone(form.cleaned_data['date'])

    def test_invalid_announcement_form(self):
        """Test that missing required fields result in errors."""
        data = {'title': '', 'message': ''}
        form = AnnouncementForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('message', form.errors)

class LeaderboardMembershipFormTests(TestCase):
    """Tests for the LeaderboardMembershipForm"""

    def test_valid_leaderboard_membership_form(self):
        """Test that valid leaderboard membership data is accepted."""
        data = {
            'membership_id': 1,
            'points': 10,
        }
        form = LeaderboardMembershipForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['membership_id'], 1)
        self.assertEqual(form.cleaned_data['points'], 10)

class LeaderboardSettingsFormTests(TestCase):
    """Tests for the LeaderboardSettingsForm"""

    def test_valid_leaderboard_settings_form(self):
        """Test that the leaderboard settings form is valid with correct data."""
        data = {
            'display_count': '5', 
            'display_points': True
        }
        form = LeaderboardSettingsForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['display_count'], '5')
        self.assertTrue(form.cleaned_data['display_points'])

    def test_invalid_display_count(self):
        """Test that an invalid display_count raises a validation error."""
        data = {
            'display_count': 'invalid',
            'display_points': False
        }
        form = LeaderboardSettingsForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('display_count', form.errors)
