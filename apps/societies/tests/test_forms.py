from django.test import TestCase
from apps.societies.forms import NewSocietyForm
from apps.societies.models import SocietyRegistration 
from apps.users.models import CustomUser
from config.constants import SOCIETY_TYPE_CHOICES


class NewSocietyFormTest(TestCase):
    """Testing for NewSocietyForm."""
    
    def setUp(self):
        """Set up a test user for SocietyRegistration"""
        self.user = CustomUser.objects.create_user(
            email="test@university.ac.uk",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="Password123"
        )
        
    def test_valid_form(self):
        """Test if the form is valid with correct data."""
        form_data = {
            'name': 'StackOverseas',
            'description': 'This is an arts club.',
            'society_type': 'arts',
            'visibility': 'Private',
        }
        form = NewSocietyForm(data=form_data)        
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_fields(self):
        """Test if the form is invalid when required fields are missing."""
        form_data = {
            'description': 'Missing name field.',
            'society_type': 'arts',
            'visibility': 'Private',
        }
        form = NewSocietyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors) 
    
    def test_invalid_form_duplicate_name(self):
        """Test if the form rejects duplicate society names."""
        SocietyRegistration.objects.create(
            name='StackOverseas',
            description='Original club.',
            society_type='arts',
            visibility='Private',
            applicant=self.user, 
        )
        form_data = {
            'name': 'StackOverseas',  
            'description': 'Traying to duplicate.',
            'society_type': 'rts',
            'visibility': 'Private',
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
        from config.constants import SOCIETY_TYPE_CHOICES
        
        form = NewSocietyForm()
        self.assertEqual(form.fields['society_type'].choices, SOCIETY_TYPE_CHOICES)

    def test_tags_parsing(self):
        """Test if tags are properly parsed into a list."""
        form_data = {
            'name': 'Arts Club',
            'description': 'A arts society',
            'society_type': 'arts',
            'visibility': 'Public',
            'tags': 'arts, ceramics, painting'
        }
        form = NewSocietyForm(data=form_data)
                 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean_tags(), ['arts', 'ceramics', 'painting'])

    def test_invalid_form_exceeding_max_length(self):
        form_data = {
            'name': 'A' * 300,  # Exceeding max length
            'description': 'Valid Description',
            'society_type': 'technology',
            'visibility': 'Public',
        }
        form = NewSocietyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_invalid_form_invalid_choice(self):
        form_data = {
            'name': 'Test Club',
            'description': 'Valid Description',
            'society_type': 'InvalidChoice',  # Invalid choice
            'visibility': 'Public',
        }
        form = NewSocietyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('society_type', form.errors)

    def test_empty_strings(self):
        form_data = {
            'name': '',
            'description': '',
            'society_type': '',
            'visibility': '',
        }
        form = NewSocietyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('description', form.errors)