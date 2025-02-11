from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages

from apps.societies.models import Society

User = get_user_model()

class CreateSocietyViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@university.ac.uk",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="secret123"
        )
        self.create_url = reverse('create_society')

    def test_redirect_if_not_logged_in(self):
        """Non-logged-in users should be redirected to login page (default Django or your custom logic)."""
        response = self.client.get(self.create_url)
        # Expect a redirect, commonly to /accounts/login or 'log_in'
        self.assertNotEqual(response.status_code, 200)
    
    def test_can_access_create_society_when_logged_in(self):
        """Logged-in users can see the create society page."""
        self.client.login(email="test@university.ac.uk", password="secret123")
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'societies/create_society.html')

    def test_can_create_new_society(self):
        """A logged-in user can create a new society if they haven't reached the limit."""
        self.client.login(email="test@university.ac.uk", password="secret123")
        post_data = {
            'name': 'Music Club',
            'description': 'We love music!',
            'society_type': 'creative',
            'base_location': 'London',
            'tags': 'music, jam sessions'
        }
        response = self.client.post(self.create_url, data=post_data)
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        # Check that the society was indeed created
        self.assertTrue(Society.objects.filter(name='Music Club').exists())
        new_soc = Society.objects.get(name='Music Club')
        self.assertEqual(new_soc.manager, self.user)
        self.assertEqual(new_soc.status, 'pending')

    def test_limit_of_3_societies_per_user(self):
        """Users who already manage 3 societies get an error and cannot create more."""
        self.client.login(email="test@university.ac.uk", password="secret123")
        # Create 3 societies
        for i in range(1, 4):
            Society.objects.create(
                name=f"Test Society {i}",
                description="Desc",
                society_type="academic",
                manager=self.user,
                status='pending'
            )
        # Now try to create the 4th
        response = self.client.post(self.create_url, {
            'name': 'Society4',
            'description': 'Another one!',
            'society_type': 'other',
            'base_location': 'somewhere',
            'tags': 'tag1, tag2'
        })
        # We expect a redirect or to stay on page with an error message
        # Because we used messages.error in the view, let's see if the code is a 302 redirect to societiespage
        self.assertEqual(response.status_code, 302)
        # The new society shouldn't exist
        self.assertFalse(Society.objects.filter(name='Society4').exists())