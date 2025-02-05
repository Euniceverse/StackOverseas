from django.tests import TestCase
from clubs.forms import NewSocietyForm

class NewSocietyFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'name': 'StackOverseas',
            'description': 'This is a coding clud.',
            'society_type': 'IT',
            'visibility': 'Private',
        }
        form = NewSocietyForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'name': 'StackOverseas',
            'description': 'This is a coding clud.',
            'society_type': 'IT',
            'visibility': 'Private',
        }
        form =  NewSocietyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_dynamic_choices(self):
        available_types = [('tech', 'Technology'), ('art', 'Art')]
        form = SocietyForm(available_types=available_types)
        self.assertEqual(form.fields['type'].choices, available_types) 

