from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages

from apps.societies.models import Society, SocietyRegistration


class SocietiesViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='test@example.ac.uk',
            password='password123',
            first_name='Test',
            last_name='User',
            preferred_name='Tester'
        )

        self.society = Society.objects.create(
            name="Tech Club",
            description="A club for tech enthusiasts",
            society_type="academic",
            manager=self.user
        )

    def test_societies_page_status_code(self):
        """Test if /societies/ page loads correctly"""
        response = self.client.get(reverse('societiespage'))
        self.assertEqual(response.status_code, 200)  # Should return HTTP 200 OK

    def test_template_used(self):
        """Test if the correct template is used"""
        response = self.client.get(reverse('societiespage'))
        self.assertTemplateUsed(response, 'societies.html')

    def test_societies_in_context(self):
        """Test if societies are passed to the template"""
        response = self.client.get(reverse('societiespage'))
        self.assertEqual(len(response.context['societies']), 1)  # Expecting 1 test society
        self.assertIn(self.society, response.context['societies'])

class TopSocietiesViewTest(TestCase):
    #create society test cases for the database
    def setUp(self):
        self.society1 = Society.objects.create(name="Chess Club", society_type="Sports", members_count=120)
        self.society2 = Society.objects.create(name="Robotics Society", society_type="Technology", members_count=80)
        self.society3 = Society.objects.create(name="Drama Club", society_type="Arts", members_count=95)
        self.society4 = Society.objects.create(name="Debate Society", society_type="Academics", members_count=110)
        self.society5 = Society.objects.create(name="Music Society", society_type="Arts", members_count=100)
        self.society6 = Society.objects.create(name="Math Club", society_type="Academics", members_count=50)

    #test if homepage loads successfully
    def test_top_societies_view_status_code(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)

    #test top 5 societies are ordered correctly
    def test_top_overall_societies(self):
        response = self.client.get(reverse('homepage'))
        top_overall = response.context['top_overall_societies']

        expected_order = [self.society1, self.society4, self.society5, self.society3, self.society2]
        self.assertEqual(list(top_overall), expected_order)

    # test grouped societies are correctly sorted and grouped by type
    def test_top_societies_per_type(self):
        response = self.client.get(reverse('homepage'))
        top_societies_per_type = response.context['top_societies_per_type']

        self.assertEqual(list(top_societies_per_type["Arts"]), [self.society5, self.society3])

        self.assertEqual(list(top_societies_per_type["Academics"]), [self.society4, self.society6])

        self.assertEqual(list(top_societies_per_type["Technology"]), [self.society2])

    # test the view when no societies
    def test_no_societies(self):
        Society.objects.all().delete()  # remove all the societies
        response = self.client.get(reverse('homepage'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['top_overall_societies']), 0)
        self.assertEqual(len(response.context['top_societies_per_type']), 0)

User = get_user_model()

class CreateSocietyViewTest(TestCase):
    """Testing for CreateSociety view."""
    
    def setUp(self):
        """Set up a test user and client."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@university.ac.uk",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="Password123"
        )
        self.create_url = reverse('create_society')

    def test_redirect_if_not_logged_in(self):
        """Non-logged-in users should be redirected to login page."""
        response = self.client.get(self.create_url)
        self.assertNotEqual(response.status_code, 200)

    def test_can_access_create_society_when_logged_in(self):
        """Logged-in users can see the create society page."""
        self.client.login(email="test@university.ac.uk", password="Password123")
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_society.html')

    def test_can_create_new_society(self):
        """A logged-in user can create a new society if they haven't reached the limit."""
        self.client.login(email="test@university.ac.uk", password="Password123")
        post_data = {
            'name': 'Music Club',
            'description': 'We love music!',
            'society_type': 'arts',
            'visibility': 'Public',
            'tags': 'music, jam sessions'
        }
        response = self.client.post(self.create_url, data=post_data)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SocietyRegistration.objects.filter(name='Music Club').exists())
        
        new_registration = SocietyRegistration.objects.get(name='Music Club')
        self.assertEqual(new_registration.applicant, self.user)
        self.assertEqual(new_registration.status, 'pending') 

    def test_limit_of_3_societies_per_user(self):
        """Users who already manage 3 societies get an error and cannot create more."""
        self.client.login(email="test@university.ac.uk", password="Password123")
        
        # create 3 societies
        for i in range(1, 4):
            Society.objects.create(
                name=f"Test Society {i}",
                description="Desc",
                society_type="academic",
                manager=self.user,
                status='approved'
            )
            
        # try to create 4th
        response = self.client.post(self.create_url, {
            'name': 'Society4',
            'description': 'Another one!',
            'society_type': 'other',
            'visibility': 'Private',
            'tags': 'tag1, tag2'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('societiespage'))
        self.assertFalse(SocietyRegistration.objects.filter(name='Society4').exists()) 

