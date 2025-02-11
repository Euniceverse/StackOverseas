from django.test import TestCase, Client
from django.urls import reverse
from societies.models import Society

class SocietiesViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test societies
        self.society1 = Society.objects.create(name="Tech Club", description="A club for tech enthusiasts.")
        self.society2 = Society.objects.create(name="Art Society", description="A place for art lovers.")

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
        self.assertEqual(len(response.context['societies']), 2)  # Expecting 2 test societies
        self.assertIn(self.society1, response.context['societies'])
        self.assertIn(self.society2, response.context['societies'])
from django.test import TestCase
from django.urls import reverse
from apps.societies.models import Society

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