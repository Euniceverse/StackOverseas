from django.test import TestCase
from apps.societies.forms import NewSocietyForm
from config.constants import SOCIETY_TYPE_CHOICES

class NewSocietyFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'name': 'StackOverseas',
            'description': 'This is a coding club.',
            'society_type': 'academic',  # Using valid choice from SOCIETY_TYPE_CHOICES
            'base_location': 'London',
            'visibility': 'Private',
        }
        form = NewSocietyForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_form(self):
        form_data = {
            'society_type': 'invalid_type',  # Invalid choice
        }
        form = NewSocietyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('base_location', form.errors)
        self.assertIn('society_type', form.errors)
        self.assertIn('name', form.errors)

    def test_society_type_choices(self):
        form = NewSocietyForm()
        self.assertEqual(
            list(form.fields['society_type'].choices),
            list(SOCIETY_TYPE_CHOICES)
        )

    def test_dynamic_choices(self):
        available_types = [('tech', 'Technology'), ('art', 'Art')]
        form = SocietyForm(available_types=available_types)
        self.assertEqual(form.fields['type'].choices, available_types)
