from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch
import json

from apps.societies import views
from apps.societies.models import Society, SocietyRegistration, Membership, MembershipRole, MembershipStatus, MembershipApplication
from apps.news.models import News
from apps.widgets.models import Widget
from apps.societies.functions import get_societies, manage_societies, get_all_users

class SocietiesViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='test1@example.ac.uk',
            password='password123',
            first_name='Test',
            last_name='User',
            preferred_name='Tester'
        )

        self.client.login(email='test1@example.ac.uk', password='password123')

        manager = get_user_model().objects.create_user(
            email='manager1@example.ac.uk',
            password='password123',
            first_name='Manager',
            last_name='One',
            preferred_name='MOne'
        )

        self.society = Society.objects.create(
            name="Tech Club",
            description="A club for tech enthusiasts",
            society_type="academic",
            status="approved",
            visibility="Public",
            manager=self.user
        )

        self.top_societies_patcher = patch(
            "apps.societies.views.top_societies",
            return_value={"top_overall_societies": [],
            "top_societies_per_type": {}}
        )
        self.mock_top_societies = self.top_societies_patcher.start()
        self.addCleanup(self.top_societies_patcher.stop)
        

        self.create_url = reverse('create_society')

    def test_societies_page_status_code(self):
        """Test if /societies/ page loads correctly"""
        response = self.client.get(reverse('societiespage'))
        self.assertEqual(response.status_code, 200)  # Should return HTTP 200 OK

    def test_fetch_societies_list(self):
        response = self.client.get(reverse('societiespage'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Tech Club", response.content.decode())


    def test_template_used(self):
        """Test if the correct template is used"""
        response = self.client.get(reverse('societiespage'))
        self.assertTemplateUsed(response, 'societies.html')

    def test_societies_in_context(self):
        """Test if societies are passed to the template"""
        response = self.client.get(reverse('societiespage'))
        self.assertEqual(len(response.context['societies']), 1)  # Expecting 1 test society
        self.assertIn(self.society, response.context['societies'])

    def test_create_society(self):
        post_data = {
            "name": "Art Club",
            "description": "A club for artists",
            "society_type": "arts",
            "visibility": "Public",
            "tags": "art, creativity"
        }
        response = self.client.post(reverse('create_society'), post_data)
        self.assertEqual(response.status_code, 302) # redirect 
        self.assertTrue(Society.objects.filter(name="Art Club").exists())
    
    def test_create_society_get(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_society.html')

    # def test_update_society(self):
    #     response = self.client.post(reverse('society-update', args=[self.society.id]), {
    #         "name": "Updated Tech Club",
    #     })
    #     self.society.refresh_from_db()
    #     self.assertEqual(self.society.name, "Updated Tech Club")

    def test_delete_society(self):
        admin = get_user_model().objects.create_superuser(
            email='adminlog@example.ac.uk',
            password='password123',
            first_name='Admin',
            last_name='User',
            preferred_name='Admin'
        )
        self.society.status = "request_delete"
        self.society.save()
        self.client.login(email='adminlog@example.ac.uk', password='password123')
        response = self.client.post(
            reverse('admin_confirm_delete', args=[self.society.id]), 
            {'action': 'approve'}
        )
        self.assertEqual(response.status_code, 302)
        updated_society = Society.objects.get(id=self.society.id)
        self.assertEqual(updated_society.status, "deleted")

    def test_join_society(self):
        response = self.client.post(reverse('society-join', args=[self.society.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.user, self.society.members.all())

    def test_update_membership_approve(self):
        """Test approving a membership."""
        other_user = get_user_model().objects.create_user(
            email='member@example.ac.uk', 
            password='password123',
            first_name='Test',
            last_name='User',
            preferred_name='Tester'
        )

        membership = Membership.objects.create(
            society=self.society, user=other_user, role=MembershipRole.MEMBER, status=MembershipStatus.PENDING)

        response = self.client.post(reverse('update_membership', args=[self.society.id, other_user.id]), {
            'action': 'approve'
        })
        
        membership.refresh_from_db()
        self.assertEqual(membership.status, MembershipStatus.APPROVED)
        self.assertRedirects(response, reverse('manage_society', args=[self.society.id]))
    
    def test_update_membership_remove(self):
        """Test removing a membership."""
        other_user = get_user_model().objects.create_user(
            email='member@example.ac.uk', 
            password='password123',
            first_name='Mem',
            last_name='Ber',
            preferred_name='Member'
        )
        membership = Membership.objects.create(
            society=self.society, user=other_user, role=MembershipRole.MEMBER, status=MembershipStatus.APPROVED)
        
        response = self.client.post(reverse('update_membership', args=[self.society.id, other_user.id]), {
            'action': 'remove'
        })
        
        self.assertFalse(Membership.objects.filter(society=self.society, user=other_user).exists())
        self.assertRedirects(response, reverse('manage_society', args=[self.society.id]))

    def test_update_membership_promote_co_manager(self):
        """Test promoting a user to Co-Manager."""
        other_user = get_user_model().objects.create_user(
            email='co_manager@example.ac.uk', 
            password='password123',
            first_name='Co',
            last_name='Manager',
            preferred_name='Co'
        )
        membership = Membership.objects.create(
            society=self.society, user=other_user, role=MembershipRole.MEMBER, status=MembershipStatus.APPROVED)
        
        response = self.client.post(reverse('update_membership', args=[self.society.id, other_user.id]), {
            'action': 'promote_co_manager'
        })
        
        membership.refresh_from_db()
        self.assertEqual(membership.role, MembershipRole.CO_MANAGER)
        self.assertEqual(membership.status, MembershipStatus.APPROVED)
        self.assertRedirects(response, reverse('manage_society', args=[self.society.id]))

    def test_update_membership_promote_editor(self):
        """Test promoting a user to Editor."""
        other_user = get_user_model().objects.create_user(
            email='editor@example.ac.uk', 
            password='password123',
            first_name='Editor',
            last_name='Test',
            preferred_name='Editor'
        )
        membership = Membership.objects.create(
            society=self.society, user=other_user, role=MembershipRole.MEMBER, status=MembershipStatus.APPROVED)
        
        response = self.client.post(reverse('update_membership', args=[self.society.id, other_user.id]), {
            'action': 'promote_editor'
        })
        
        membership.refresh_from_db()
        self.assertEqual(membership.role, MembershipRole.EDITOR)
        self.assertEqual(membership.status, MembershipStatus.APPROVED)
        self.assertRedirects(response, reverse('manage_society', args=[self.society.id]))

    # def test_return_form_on_get_request(self):
    #     response = self.client.get(reverse('update_membership', args=[self.society.id, self.user.id]))
    #     # Since view renders update_membership.html on GET
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "update_membership.html")


    def test_societiespage_loads_successfully(self):
        response = self.client.get(reverse("societiespage"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "societies.html")
    
    def test_my_societies_authenticated_user(self):
        Membership.objects.create(user=self.user, society=self.society)
        
        response = self.client.get(reverse("my_societies"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "societies.html")
        societies = list(response.context["societies"].values_list("name", flat=True))
        self.assertEqual(set(societies), {"Tech Club"})
    
    def test_my_societies_no_memberships(self):
        Membership.objects.filter(user=self.user).delete()
        response = self.client.get(reverse("my_societies"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "societies.html")
        self.assertEqual(len(response.context["societies"]), 1)
    
    def test_my_societies_news_list(self):
        Membership.objects.create(user=self.user, society=self.society)
        
        News.objects.create(title="Test News", content="Content", is_published=True, date_posted=timezone.now(), society=self.society)
        response = self.client.get(reverse("my_societies"))
        self.assertIn("news_list", response.context)
        self.assertEqual(len(response.context["news_list"]), 1)
        self.assertEqual(response.context["news_list"][0].title, "Test News")

    def test_societiespage_loads(self):
        url = reverse('societiespage')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("societies", response.context)
        self.assertIn(self.society, response.context['societies'])

    
    def test_societiespage_sorting(self):
    
        manager = get_user_model().objects.create_user(
            email='manager4@example.ac.uk',
            password='password123',
            first_name='Manager',
            last_name='One',
            preferred_name='MOne'
        )

        soc2 = Society.objects.create(
            name="Alpha Club",
            description="Another club",
            society_type="academic",
            status="approved",
            manager=manager
        )

        url = reverse('societiespage') + "?sort=name_asc"
        response = self.client.get(url)
        names = [soc.name for soc in response.context['societies']]
        self.assertEqual(names, sorted(names))




class TopSocietiesViewTest(TestCase):
    #create society test cases for the database
    def setUp(self):
        manager = get_user_model().objects.create_user(
            email='manager5@example.ac.uk',
            password='password123',
            first_name='Manager',
            last_name='One',
            preferred_name='MOne'
        )
        self.client.login(email='manager5@example.ac.uk', password='password123')

        self.society1 = Society.objects.create(
            name="Chess Club", 
            society_type="sports", 
            members_count=120, 
            manager=manager,
            status="approved"
        )
        self.society2 = Society.objects.create(
            name="Robotics Society", 
            society_type="technology", 
            members_count=80, 
            manager=manager,
            status="approved"
        )
        self.society3 = Society.objects.create(
            name="Drama Club", 
            society_type="arts", 
            members_count=101, 
            manager=manager,
            status="approved"
        )
        self.society4 = Society.objects.create(
            name="Debate Society", 
            society_type="academics", 
            members_count=110, 
            manager=manager,
            status="approved"
        )
        self.society5 = Society.objects.create(
            name="Music Society", 
            society_type="arts", 
            members_count=100, 
            manager=manager,
            status="approved"
        )
        self.society6 = Society.objects.create(
            name="Math Club", 
            society_type="academics", 
            members_count=50, 
            manager=manager,
            status="approved"
        )

        Membership.objects.create(
            society=self.society3,
            user=manager,
            status=MembershipStatus.APPROVED,
            role=MembershipRole.MANAGER
        )
        Membership.objects.create(
            society=self.society5,
            user=manager,
            status=MembershipStatus.APPROVED,
            role=MembershipRole.MANAGER
        )


    #test if homepage loads successfully
    def test_top_societies_view_status_code(self):
        response = self.client.get(reverse('societiespage'))
        self.assertEqual(response.status_code, 200)

    #test top 5 societies are ordered correctly
    # def test_top_overall_societies(self):
    #     response = self.client.get(reverse('societiespage'))
    #     top_overall = response.context['top_overall_societies']

    #     expected_order = [self.society1, self.society4, self.society5, self.society3, self.society2]
    #     self.assertEqual(list(top_overall), expected_order)

    # test grouped societies are correctly sorted and grouped by type
    @patch("apps.societies.views.top_societies",
           return_value={
               "top_overall_societies": [],
               "top_societies_per_type": {
                   "arts": [], 
                   "academics": [],
                   "technology": []
               }
           })
    def test_top_societies_per_type(self, mock_top):
        expected = {
            "top_overall_societies": [],
            "top_societies_per_type": {
                "arts": [self.society3, self.society5],
                "academics": [self.society4, self.society6],
                "technology": [self.society2]
            }
        }
        mock_top.return_value = expected
        
        response = self.client.get(reverse('societiespage'))
        top_societies_per_type = response.context['top_societies_per_type']

        self.assertEqual(list(top_societies_per_type["arts"]), [self.society3, self.society5])

        self.assertEqual(list(top_societies_per_type["academics"]), [self.society4, self.society6])

        self.assertEqual(list(top_societies_per_type["technology"]), [self.society2])

    # test the view when no societies
    def test_no_societies(self):
        with patch("apps.societies.views.top_societies", return_value={"top_overall_societies": [], "top_societies_per_type": {}}):
            Society.objects.all().delete()  # remove all the societies
            response = self.client.get(reverse('societiespage'))
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
        self.client.login(email="test@university.ac.uk", password="Password123")
        self.create_url = reverse('create_society')

    def test_redirect_if_not_logged_in(self):
        """Non-logged-in users should be redirected to login page."""
        self.client.logout()
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
    
    def test_create_society_post_success(self):
        post_data = {
            'name': 'Art Club',
            'description': 'A club for artists',
            'society_type': 'arts',
            'visibility': 'Public',
        }
        response = self.client.post(self.create_url, data=post_data)
        # Expect redirect
        self.assertEqual(response.status_code, 302)
        # Check that a SocietyRegistration and Society were created
        self.assertTrue(SocietyRegistration.objects.filter(name='Art Club').exists())

    def test_limit_of_3_societies_per_user(self):
        """Users who already manage 3 societies get an error and cannot create more."""
        self.client.login(email="test@university.ac.uk", password="Password123")
        
        # create 3 societies
        for i in range(1, 4):
            # manager = get_user_model().objects.create_user(
            #     email=f'manager{i}@example.ac.uk',
            #     password='password123',
            #     first_name='Manager',
            #     last_name='One',
            #     preferred_name='MOne'
            # )

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
            'society_type': 'other'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('societiespage'))
        self.assertFalse(SocietyRegistration.objects.filter(name='Society4').exists()) 

    def test_create_society_limit_reached(self):
        # Create 3 societies managed by this user
        for i in range(3):
            # manager = get_user_model().objects.create_user(
            #     email=f'manager{i}@example.ac.uk',
            #     password='password123',
            #     first_name='Manager',
            #     last_name='One',
            #     preferred_name='MOne'
            # )
            
            Society.objects.create(
                name=f"Test Society {i}",
                description="Desc",
                society_type="academic",
                manager=self.user,
                status='approved'
            )
        post_data = {
            'name': 'Society 4',
            'description': 'Should fail',
            'society_type': 'other',
            'visibility': 'Private',
            'tags': 'tag'
        }
        response = self.client.post(self.create_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        # No SocietyRegistration should be created for Society 4
        self.assertFalse(Society.objects.filter(name='Society 4').exists())

class ApplicationManagementTest(TestCase):
    def setUp(self):
        """Set up a test user and client."""
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email="test2@university.ac.uk",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="Password123"
        )
        self.manager = get_user_model().objects.create_user(
            email="manager@university.ac.uk",
            password="ManagerPass",
            first_name="Manager",
            last_name="Person",
            preferred_name="Manage"
        )
        self.society = Society.objects.create(
            name="AI Club",
            description="A club for AI enthusiasts",
            society_type="academic",
            status="approved",
            manager=self.manager
        )
        self.application = MembershipApplication.objects.create(
            user=self.user, society=self.society, is_approved=False, is_rejected=False
        )
        self.client.login(email="manager@university.ac.uk", password="ManagerPass")
    
    def test_view_applications_as_manager(self):
        response = self.client.get(reverse("view_applications", args=[self.society.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_applications.html")
        self.assertIn("applications", response.context)
    
    def test_view_applications_no_permission(self):
        self.client.login(email="test2@university.ac.uk", password="Password123")
        response = self.client.get(reverse("view_applications", args=[self.society.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_decide_application_approve(self):
        response = self.client.post(reverse("decide_application", args=[self.society.id, self.application.id, "approve"]))
        self.application.refresh_from_db()
        self.assertTrue(self.application.is_approved)
        self.assertRedirects(response, reverse("view_applications", args=[self.society.id]))
    
    def test_decide_application_reject(self):
        response = self.client.post(reverse("decide_application", args=[self.society.id, self.application.id, "reject"]))
        self.application.refresh_from_db()
        self.assertTrue(self.application.is_rejected)
        self.assertRedirects(response, reverse("view_applications", args=[self.society.id]))
    
    def test_decide_application_invalid_action(self):
        response = self.client.post(reverse("decide_application", args=[self.society.id, self.application.id, "invalid"]))
        self.assertRedirects(response, reverse("view_applications", args=[self.society.id]))

class RequestDeleteSocietyTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@uni.ac.uk", 
            password="password123",
            first_name='Test',
            last_name='User',
            preferred_name='Test'
        )

        self.small_society = Society.objects.create(
            name="Small Society",
            members_count=50,
            status="approved",
            visibility="Public",
            manager=self.user
        )

        self.large_society = Society.objects.create(
            name="Large Society",
            members_count=150,
            status="approved",
            visibility="Public",
            manager=self.user
        )

        self.url_small = reverse("request_delete_society", args=[self.small_society.id])
        self.url_large = reverse("request_delete_society", args=[self.large_society.id])

    def test_get_request_delete_page(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(self.url_small)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "request_delete_society.html")
        self.assertContains(response, "Are you sure you want to request the deletion")

    def test_post_delete_small_society(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(self.url_small)

        # check if society is marked as deleted
        self.small_society.refresh_from_db()
        self.assertEqual(self.small_society.status, "deleted")

        self.assertRedirects(response, reverse("societiespage"))

    def test_post_delete_large_society(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(self.url_large)
        self.large_society.refresh_from_db()
        self.assertEqual(self.large_society.status, "request_delete")
        self.assertEqual(self.large_society.visibility, "Private")
        self.assertRedirects(response, reverse("societiespage"))

    def test_unauthorized_user_cannot_delete(self):
        other_user = User.objects.create_user(
            email="otheruser@uni.ac.uk",
            first_name='Other',
            last_name='User',
            preferred_name='Other',
            password="password123"
        )
        self.client.login(username="otheruser", password="password123")
        response = self.client.post(self.url_small)
        self.small_society.refresh_from_db()
        self.assertEqual(self.small_society.status, "approved") 
        self.assertEqual(response.status_code, 403)


class ManageSocietiesAndMembersTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='test2@example.ac.uk',
            password='password123',
            first_name='Test',
            last_name='User',
            preferred_name='Tester'
        )
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.ac.uk',
            password='adminpass',
            first_name='Admin',
            last_name='User',
            preferred_name='Admin'
        )
        self.client.login(email='test2@example.ac.uk', password='password123')

        self.society = Society.objects.create(
            name="Tech Club",
            description="A club for tech enthusiasts",
            society_type="academic",
            status="pending",
            manager=self.user
        )
    
    # def test_view_manage_societies_authenticated(self):
    #     response = self.client.get(reverse("view_manage_societies"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "societies.html")
    #     self.assertIn("societies", response.context)
    
    @patch("apps.news.models.News.objects.filter")
    def test_view_manage_societies_with_news(self, mock_news_filter):
        dummy_news = News(id=1, title="Tech News", content="dummy content", is_published=True, date_posted=timezone.now())
        mock_news_filter.return_value.order_by.return_value = [dummy_news]
        response = self.client.get(reverse("manage_societies"))
        self.assertTrue(response.context.get("news_list"))
        self.assertEqual(len(response.context["news_list"]), 1)
        self.assertEqual(response.context["news_list"][0].title, "Tech News")
    
    def test_view_all_members_superuser(self):
        self.client.login(email='admin@example.ac.uk', password='adminpass')
        response = self.client.get(reverse("view_all_members"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manage_society.html")
    
    def test_view_all_members_non_admin(self):
        response = self.client.get(reverse("view_all_members"))
        self.assertEqual(response.status_code, 302)  # Redirect due to permission error


class MembershipAndSocietyTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='test3@example.ac.uk',
            password='password123',
            first_name='Test',
            last_name='User',
            preferred_name='Tester'
        )
        self.manager = get_user_model().objects.create_user(
            email='manager@example.ac.uk',
            password='managerpass',
            first_name='Manager',
            last_name='Test',
            preferred_name='Manager'
        )
        self.society = Society.objects.create(
            name="Tech Club",
            description="A club for tech enthusiasts",
            society_type="academic",
            status="approved",
            manager=self.manager
        )
        self.membership = Membership.objects.create(
            society=self.society, user=self.user, status=MembershipStatus.PENDING
        )
        self.client.login(email='manager@example.ac.uk', password='managerpass')

    def test_update_membership_approve(self):
        response = self.client.post(reverse("update_membership", args=[self.society.id, self.user.id]), {"action": "approve"})
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.status, MembershipStatus.APPROVED)
        self.assertRedirects(response, reverse("manage_society", args=[self.society.id]))
    
    def test_update_membership_remove(self):
        response = self.client.post(reverse("update_membership", args=[self.society.id, self.user.id]), {"action": "remove"})
        self.assertFalse(Membership.objects.filter(id=self.membership.id).exists())
        self.assertRedirects(response, reverse("manage_society", args=[self.society.id]))
    
    def test_update_membership_no_permission(self):
        self.client.login(email='test3@example.ac.uk', password='password123')
        response = self.client.post(reverse("update_membership", args=[self.society.id, self.user.id]), {"action": "approve"})
        self.assertEqual(response.status_code, 302)
    
    # def test_society_detail(self):
    #     response = self.client.get(reverse("society_detail", args=[self.society.id]))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "society_detail.html")
    #     self.assertIn("society", response.context)
    
    def test_join_society_already_member(self):
        self.membership.status = MembershipStatus.APPROVED
        self.membership.save()
        response = self.client.get(reverse("join_society", args=[self.society.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "join_society.html")

    def test_join_society_new_application(self):
        self.client.login(email='test3@example.ac.uk', password='password123')
        response = self.client.post(reverse("join_society", args=[self.society.id]), {})
        self.assertRedirects(response, reverse("society_page", args=[self.society.id]))



class SocietyDeletionAndWidgetsTest(TestCase):
    def setUp(self):
        """Set up a test user and client."""
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email="test3@university.ac.uk",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="Password123"
        )
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@university.ac.uk",
            password="AdminPass",
            first_name='The',
            last_name='Admin',
            preferred_name='Boss'
        )
        self.society = Society.objects.create(
            name="AI Club",
            description="A club for AI enthusiasts",
            society_type="academic",
            status="approved",
            manager=self.user,
            members_count=50
        )
        self.widget = Widget.objects.create(society=self.society, widget_type="events", position=1)
        self.client.login(email="test3@university.ac.uk", password="Password123")
    
    def test_request_delete_society_auto_delete(self):
        self.society.members_count = 50  # Less than 100 for auto-delete
        self.society.save()
        response = self.client.post(reverse("request_delete_society", args=[self.society.id]))
        self.society.refresh_from_db()
        self.assertEqual(self.society.status, "deleted")
        self.assertRedirects(response, reverse("societiespage"))
    
    def test_request_delete_society_admin_approval(self):
        self.society.members_count = 150  # More than 100 for admin approval
        self.society.save()
        response = self.client.post(reverse("request_delete_society", args=[self.society.id]))
        self.society.refresh_from_db()
        self.assertEqual(self.society.status, "request_delete")
        self.assertRedirects(response, reverse("societiespage"))
    
    def test_admin_confirm_delete_approve(self):
        self.client.login(email="admin@university.ac.uk", password="AdminPass")
        self.society.status = "request_delete"
        self.society.save()
        response = self.client.post(reverse("admin_confirm_delete", args=[self.society.id]), {"action": "approve"})
        self.society.refresh_from_db()
        self.assertEqual(self.society.status, "deleted")
        self.assertRedirects(response, reverse("societiespage"))
    
    def test_admin_confirm_delete_reject(self):
        self.client.login(email="admin@university.ac.uk", password="AdminPass")
        self.society.status = "request_delete"
        self.society.save()
        response = self.client.post(reverse("admin_confirm_delete", args=[self.society.id]), {"action": "reject"})
        self.society.refresh_from_db()
        self.assertEqual(self.society.status, "approved")
        self.assertRedirects(response, reverse("societiespage"))
    
    def test_society_admin_view_permission(self):
        response = self.client.get(reverse("society_admin_view", args=[self.society.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "society_admin.html")
    
    def test_society_admin_view_no_permission(self):
        another_user = get_user_model().objects.create_user(
            email="another@uni.ac.uk", 
            password="pass",
            first_name="Another",
            last_name="User",
            preferred_name="Another"
        )
        self.client.login(email="another@uni.ac.uk", password="pass")
        response = self.client.get(reverse("society_admin", args=[self.society.id]))
        self.assertEqual(response.status_code, 302)  # Redirect due to permission error
    
    def test_society_page_view(self):
        response = self.client.get(reverse("society_page", args=[self.society.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "society_page.html")

class MySocietiesViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="user2@uni.ac.uk",
            password="pass123",
            first_name="User",
            last_name="Two",
            preferred_name="U2"
        )
        self.client.login(email="user2@uni.ac.uk", password="pass123")
        # Create a society where user is a member
        self.society = Society.objects.create(
            name="Member Club",
            description="Society where user is member",
            society_type="academic",
            status="approved",
            manager=self.user
        )
        Membership.objects.create(
            society=self.society, 
            user=self.user, 
            status=MembershipStatus.APPROVED
        )
        
        # Create some dummy news
        News.objects.create(
            title="News 1", 
            content="Content", 
            is_published=True, 
            date_posted=timezone.now(),
            society=self.society
        )
    
    def test_my_societies_loads(self):
        url = reverse('my_societies')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check that both societies and news_list are present in context
        self.assertIn("societies", response.context)
        self.assertIn("news_list", response.context)

        # Since user is member, society should be in list
        self.assertIn(self.society, response.context['societies'])

class AdminViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.regular_user = User.objects.create_user(
            email="reg@uni.ac.uk",
            password="pass",
            first_name='Reg',
            last_name='Test',
            preferred_name='Reg'
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@uni.ac.uk",
            password="adminpass",
            first_name='Admin2',
            last_name='Another',
            preferred_name='Two'
        )
        # Create a pending society
        self.pending_society = Society.objects.create(
            name="Pending Club",
            description="Needs approval",
            society_type="academic",
            manager=self.regular_user,
            status="pending"
        )
        self.approve_url = reverse('admin_confirm_society_decision', kwargs={
            'society_id': self.pending_society.id,
            'action': 'approve'
        })
        self.reject_url = reverse('admin_confirm_society_decision', kwargs={
            'society_id': self.pending_society.id,
            'action': 'reject'
        })
        self.pending_url = reverse('admin_pending_societies')
    
    def test_non_admin_cannot_view_pending(self):
        self.client.login(email="reg@uni.ac.uk", password="pass")
        response = self.client.get(self.pending_url)
        self.assertNotEqual(response.status_code, 200)
    
    def test_admin_can_view_pending(self):
        self.client.login(email="admin@uni.ac.uk", password="adminpass")
        response = self.client.get(self.pending_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending Club")
    
    def test_admin_approve_society(self):
        self.client.login(email="admin@uni.ac.uk", password="adminpass")
        # GET confirmation page
        response = self.client.get(self.approve_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure")
        # POST to approve
        response = self.client.post(self.approve_url, {'confirm': True})
        self.assertEqual(response.status_code, 302)
        self.pending_society.refresh_from_db()
        self.assertEqual(self.pending_society.status, 'approved')
    
    def test_admin_reject_society(self):
        self.client.login(email="admin@uni.ac.uk", password="adminpass")
        response = self.client.post(self.reject_url, {'confirm': True})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Society.objects.filter(id=self.pending_society.id).exists())
    
    def test_admin_cancel_action(self):
        self.client.login(email="admin@uni.ac.uk", password="adminpass")
        response = self.client.post(self.approve_url, {'cancel': True})
        self.assertEqual(response.status_code, 302)
        self.pending_society.refresh_from_db()
        self.assertEqual(self.pending_society.status, 'pending')

class ManageSocietyViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = User.objects.create_user(
            email="mgr@uni.ac.uk",
            password="pass",
            first_name='Manage',
            last_name='University',
            preferred_name='Manager'
        )
        self.normal = User.objects.create_user(
            email="norm@uni.ac.uk",
            password="pass",
            first_name='Norm',
            last_name='Normal',
            preferred_name='Norm'
        )
        self.society = Society.objects.create(
            name="Manage Club",
            description="For management",
            society_type="academic",
            status="approved",
            manager=self.manager
        )
        # Create memberships for normal user and a co-manager
        Membership.objects.create(
            society=self.society,
            user=self.normal,
            role=MembershipRole.MEMBER,
            status=MembershipStatus.PENDING
        )
        self.co_manager = User.objects.create_user(
            email="comgr@uni.ac.uk",
            password="pass",
            first_name='Co',
            last_name='Manager',
            preferred_name='Co'
        )
        Membership.objects.create(
            society=self.society,
            user=self.co_manager,
            role=MembershipRole.CO_MANAGER,
            status=MembershipStatus.APPROVED
        )
        self.manage_url = reverse('manage_society', args=[self.society.id])
    
    def test_manager_can_access_manage_page(self):
        self.client.login(email="mgr@uni.ac.uk", password="pass")
        response = self.client.get(self.manage_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manage Society")
        # Expect to see memberships for co_manager and normal user
        self.assertContains(response, self.normal.email)
        self.assertContains(response, self.co_manager.email)
    
    def test_non_authorized_user_cannot_access_manage_page(self):
        self.client.login(email="norm@uni.ac.uk", password="pass")
        response = self.client.get(self.manage_url)
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [302, 403])

class UpdateMembershipViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = User.objects.create_user(
            email="mgr2@uni.ac.uk",
            password="pass",
            first_name='Manager',
            last_name='Two',
            preferred_name='Manager'
        )
        self.other = User.objects.create_user(
            email="other@uni.ac.uk",
            password="pass",
            first_name='Other',
            last_name='User',
            preferred_name='Other User'
        )
        self.society = Society.objects.create(
            name="Update Club",
            description="Club for updates",
            society_type="academic",
            status="approved",
            manager=self.manager
        )
        self.membership = Membership.objects.create(
            society=self.society,
            user=self.other,
            role=MembershipRole.MEMBER,
            status=MembershipStatus.PENDING
        )
        self.update_url = reverse('update_membership', args=[self.society.id, self.other.id])
    
    def test_approve_membership(self):
        self.client.login(email="mgr2@uni.ac.uk", password="pass")
        response = self.client.post(self.update_url, {'action': 'approve'}, follow=True)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.status, MembershipStatus.APPROVED)
    
    def test_remove_membership(self):
        self.client.login(email="mgr2@uni.ac.uk", password="pass")
        response = self.client.post(self.update_url, {'action': 'remove'}, follow=True)
        self.assertFalse(Membership.objects.filter(id=self.membership.id).exists())
    
    def test_promote_to_co_manager(self):
        self.client.login(email="mgr2@uni.ac.uk", password="pass")
        response = self.client.post(self.update_url, {'action': 'promote_co_manager'}, follow=True)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.role, MembershipRole.CO_MANAGER)
    
    def test_promote_to_editor(self):
        self.client.login(email="mgr2@uni.ac.uk", password="pass")
        response = self.client.post(self.update_url, {'action': 'promote_editor'}, follow=True)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.role, MembershipRole.EDITOR)
    
    # def test_get_request_redirects(self):
    #     self.client.login(email="mgr2@uni.ac.uk", password="pass")
    #     response = self.client.get(self.update_url)
    #     self.assertRedirects(response, reverse('manage_society', args=[self.society.id]))

    def test_get_request_returns_form(self):
        self.client.login(email="mgr2@uni.ac.uk", password="pass")
        response = self.client.get(reverse('update_membership', args=[self.society.id, self.other.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "update_membership.html")

class JoinSocietyViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="join@uni.ac.uk",
            password="pass",
            first_name='Join',
            last_name='Test',
            preferred_name='Join'
        )
        self.society = Society.objects.create(
            name="Join Club",
            description="For joining",
            society_type="academic",
            status="approved",
            manager=self.user
        )
        self.join_url = reverse('join_society', args=[self.society.id])
    
    def test_join_get_returns_form(self):
        self.client.login(email="join@uni.ac.uk", password="pass")
        response = self.client.get(self.join_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "join_society.html")
    
    def test_join_post_creates_application(self):
        self.client.login(email="join@uni.ac.uk", password="pass")
        # For a society with no extra requirement, auto-approve join
        response = self.client.post(self.join_url, {})
        self.assertRedirects(response, reverse('society_page', args=[self.society.id]))
        # Membership should be auto-approved
        membership = Membership.objects.get(society=self.society, user=self.user)
        self.assertEqual(membership.status, MembershipStatus.APPROVED)
    
    def test_join_already_member_redirects_post(self):
        Membership.objects.create(
            society=self.society,
            user=self.user,
            status=MembershipStatus.APPROVED
        )
        self.client.login(email="join@uni.ac.uk", password="pass")
        response = self.client.post(reverse('join_society', args=[self.society.id]), {})
        detail_url = reverse('society_page', args=[self.society.id]) # redirect to society page
        self.assertRedirects(response, detail_url)
        # Ensure no duplicate membership is created.
        memberships = Membership.objects.filter(user=self.user, society=self.society)
        self.assertEqual(memberships.count(), 1)

    def test_join_already_member_redirects_get(self):
        Membership.objects.create(
            society=self.society,
            user=self.user,
            status=MembershipStatus.APPROVED
        )
        self.client.login(email="join@uni.ac.uk", password="pass")
        response = self.client.get(reverse('join_society', args=[self.society.id]))
        # Expect code 200 and join_society
        self.assertEqual(response.status_code, 302)
        detail_url = reverse('society_page', args=[self.society.id])
        self.assertRedirects(response, detail_url)

class ViewApplicationsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = User.objects.create_user(
            email="appmgr@uni.ac.uk",
            password="pass",
            first_name='Applicant',
            last_name='Manager',
            preferred_name='App',
        )
        self.applicant = User.objects.create_user(
            email="applicant@uni.ac.uk",
            password="pass",
            first_name='Applicant',
            last_name='Test',
            preferred_name='Applicant'
        )
        self.society = Society.objects.create(
            name="App Club",
            description="For applications",
            society_type="academic",
            status="approved",
            manager=self.manager
        )
        # Create a pending application and membership
        self.application = MembershipApplication.objects.create(
            user=self.applicant,
            society=self.society,
            essay_text="I want to join.",
            is_approved=False,
            is_rejected=False
        )
        self.membership = Membership.objects.create(
            society=self.society,
            user=self.applicant,
            role=MembershipRole.MEMBER,
            status=MembershipStatus.PENDING
        )
        self.view_apps_url = reverse('view_applications', args=[self.society.id])
    
    def test_view_applications_authorized(self):
        self.client.login(email="appmgr@uni.ac.uk", password="pass")
        response = self.client.get(self.view_apps_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_applications.html")
        self.assertIn("applications", response.context)
    
    def test_view_applications_unauthorized(self):
        self.client.login(email="applicant@uni.ac.uk", password="pass")
        response = self.client.get(self.view_apps_url)
        self.assertNotEqual(response.status_code, 200)
    
    def test_decide_application_approve(self):
        self.client.login(email="appmgr@uni.ac.uk", password="pass")
        decide_url = reverse('decide_application', args=[self.society.id, self.application.id, "approve"])
        response = self.client.post(decide_url)
        self.application.refresh_from_db()
        self.assertTrue(self.application.is_approved)
        # Membership should be updated to approved
        mem = Membership.objects.get(society=self.society, user=self.applicant)
        self.assertEqual(mem.status, MembershipStatus.APPROVED)
    
    def test_decide_application_reject(self):
        self.client.login(email="appmgr@uni.ac.uk", password="pass")
        decide_url = reverse('decide_application', args=[self.society.id, self.application.id, "reject"])
        response = self.client.post(decide_url)
        self.application.refresh_from_db()
        self.assertTrue(self.application.is_rejected)
        # Membership should be removed
        self.assertFalse(Membership.objects.filter(society=self.society, user=self.applicant).exists())
    
    def test_decide_application_invalid(self):
        self.client.login(email="appmgr@uni.ac.uk", password="pass")
        decide_url = reverse('decide_application', args=[self.society.id, self.application.id, "invalid"])
        response = self.client.post(decide_url)
        self.assertRedirects(response, self.view_apps_url)

class RequestDeleteSocietyTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="reqdel@uni.ac.uk",
            password="pass",
            first_name='Request',
            last_name='Delete',
            preferred_name='Request'
        )
        self.society_small = Society.objects.create(
            name="Small Society",
            members_count=50,
            status="approved",
            visibility="Public",
            manager=self.user
        )
        self.society_large = Society.objects.create(
            name="Large Society",
            members_count=150,
            status="approved",
            visibility="Public",
            manager=self.user
        )
        self.url_small = reverse("request_delete_society", args=[self.society_small.id])
        self.url_large = reverse("request_delete_society", args=[self.society_large.id])
    
    def test_get_request_delete_page(self):
        self.client.login(email="reqdel@uni.ac.uk", password="pass")
        response = self.client.get(self.url_small)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "request_delete_society.html")
        self.assertContains(response, "Are you sure")
    
    def test_post_delete_small_society(self):
        self.client.login(email="reqdel@uni.ac.uk", password="pass")
        response = self.client.post(self.url_small)
        self.society_small.refresh_from_db()
        self.assertEqual(self.society_small.status, "deleted")
        self.assertRedirects(response, reverse("societiespage"))
    
    def test_post_delete_large_society(self):
        self.client.login(email="reqdel@uni.ac.uk", password="pass")
        response = self.client.post(self.url_large)
        self.society_large.refresh_from_db()
        self.assertEqual(self.society_large.status, "request_delete")
        self.assertEqual(self.society_large.visibility, "Private")
        self.assertRedirects(response, reverse("societiespage"))

class AdminConfirmDeleteTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            email="admin2@uni.ac.uk",
            password="pass",
            first_name='Admin',
            last_name='Two',
            preferred_name='Ad'
        )
        self.user = User.objects.create_user(
            email="user@uni.ac.uk",
            password="pass",
            first_name='User',
            last_name='Test',
            preferred_name='User'
        )
        self.society = Society.objects.create(
            name="Delete Society",
            status="request_delete",
            manager=self.user
        )
        self.create_url = reverse("admin_confirm_delete", args=[self.society.id])
    
    def test_admin_approve_delete(self):
        self.client.login(email="admin2@uni.ac.uk", password="pass")
        response = self.client.post(self.create_url, {"action": "approve"})
        self.society.refresh_from_db()
        self.assertEqual(self.society.status, "deleted")
        self.assertRedirects(response, reverse("societiespage"))
    
    def test_admin_reject_delete(self):
        self.client.login(email="admin2@uni.ac.uk", password="pass")
        response = self.client.post(self.create_url, {"action": "reject"})
        self.society.refresh_from_db()
        self.assertEqual(self.society.status, "approved")
        self.assertRedirects(response, reverse("societiespage"))
    
    def test_get_admin_confirm_delete_page(self):
        self.client.login(email="admin2@uni.ac.uk", password="pass")
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_confirm_delete.html")

class SocietyAdminViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = User.objects.create_user(
            email='adminview@uni.ac.uk',
            password='pass',
            first_name='Admin',
            last_name='View',
            preferred_name='Admin'
        )
        self.other = User.objects.create_user(
            email='other@uni.ac.uk',
            password='pass',
            first_name='Other',
            last_name='User',
            preferred_name='Other'
        )
        self.society = Society.objects.create(
            name="Admin View Society",
            status="approved",
            manager=self.manager
        )
        self.create_url = reverse("society_admin_view", args=[self.society.id])
    
    def test_admin_view_permission(self):
        self.client.login(email="adminview@uni.ac.uk", password="pass")
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "society_admin.html")
    
    def test_admin_view_no_permission(self):
        self.client.login(email="other@uni.ac.uk", password="pass")
        response = self.client.get(self.create_url)
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [302, 403])



class SocietyPageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="public@uni.ac.uk",
            password="pass",
            first_name="Public",
            last_name="User",
            preferred_name="Public"
        )
        self.society = Society.objects.create(
            name="Public Society",
            description="Public info",
            society_type="academic",
            status="approved",
            manager=self.user
        )
        # Create some memberships and widgets
        Membership.objects.create(society=self.society, user=self.user, status=MembershipStatus.APPROVED)
        self.widget = Widget.objects.create(society=self.society, widget_type="news", position=0)
        self.create_url = reverse("society_page", args=[self.society.id])
    
    def test_society_page_loads(self):
        self.client.login(email="public@uni.ac.uk", password="pass")
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "society_page.html")
        self.assertIn("society", response.context)
        self.assertIn("members_count", response.context)
    
    def test_society_page_context_membership(self):
        self.client.login(email="public@uni.ac.uk", password="pass")
        response = self.client.get(self.create_url)
        # Check that if the logged-in user is a member, user_membership is in context
        self.assertIn("user_membership", response.context)
    

class LeaveSocietyViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="leaver@uni.ac.uk",
            password="pass",
            first_name="Leaver",
            last_name="Test",
            preferred_name="Leaver"
        )
        self.society = Society.objects.create(
            name="Leave Society",
            status="approved",
            manager=self.user
        )
        self.membership = Membership.objects.create(
            society=self.society,
            user=self.user,
            status=MembershipStatus.APPROVED
        )
        self.create_url = reverse("leave_society", args=[self.society.id])
    
    def test_leave_society_get(self):
        """GET should render a confirmation page."""
        self.client.login(email="leaver@uni.ac.uk", password="pass")
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "confirm_leave.html")
    
    def test_leave_society_post(self):
        self.client.login(email="leaver@uni.ac.uk", password="pass")
        response = self.client.post(self.create_url)
        self.assertRedirects(response, reverse("society_page", args=[self.society.id]))
        self.assertFalse(Membership.objects.filter(id=self.membership.id).exists())
    
    def test_leave_society_not_member(self):
        # Remove membership first
        self.membership.delete()
        self.client.login(email="leaver@uni.ac.uk", password="pass")
        response = self.client.post(self.create_url)
        self.assertRedirects(response, reverse("society_page", args=[self.society.id]))
        

class SocietiesUrlsTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_societiespage_url(self):
        url = reverse('societiespage')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.societiespage)
    
    def test_create_society_url(self):
        url = reverse('create_society')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.create_society)
    
    def test_join_society_url(self):
        url = reverse('join_society', args=[1])
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.join_society)
    
    def test_admin_confirm_delete_url(self):
        url = reverse('admin_confirm_delete', args=[1])
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.admin_confirm_delete)


User = get_user_model()

class ExtraViewsTest(TestCase):
    def setUp(self):
        # Create a manager and a normal user.
        self.client = Client()
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="managerpass",
            first_name="Manager",
            last_name="Test",
            preferred_name="Manager"
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            password="userpass",
            first_name="User",
            last_name="Test",
            preferred_name="User"
        )
        # Create an approved society with manager as creator.
        self.society = Society.objects.create(
            name="Extra Society",
            description="For extra tests",
            society_type="academic",
            status="approved",
            visibility="Public",
            manager=self.manager
        )
        # Add a membership for manager (so that some views check membership).
        Membership.objects.create(
            society=self.society,
            user=self.manager,
            role=MembershipRole.MANAGER,
            status=MembershipStatus.APPROVED
        )

    def test_update_membership_get_returns_form(self):
        """
        Test that a GET request to update_membership returns the update form.
        """
        # Create a pending membership for the user.
        membership = Membership.objects.create(
            society=self.society,
            user=self.user,
            role=MembershipRole.MEMBER,
            status=MembershipStatus.PENDING
        )
        self.client.login(email="manager@example.com", password="managerpass")
        url = reverse("update_membership", args=[self.society.id, self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "update_membership.html")

    def test_view_manage_societies_empty_news(self):
        """
        Test that view_manage_societies returns an empty news list when there is no news.
        """
        self.client.login(email="manager@example.com", password="managerpass")
        url = reverse("manage_societies")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # news_list should be in context, but empty if there are no published news.
        self.assertIn("news_list", response.context)
        self.assertEqual(len(response.context["news_list"]), 0)

    def test_admin_pending_societies_view(self):
        """
        Test that the admin_pending_societies view shows pending societies.
        """
        # Create a pending society.
        pending_society = Society.objects.create(
            name="Pending Society",
            description="Pending for admin",
            society_type="academic",
            status="pending",
            visibility="Private",
            manager=self.user
        )
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass",
            first_name="Admin",
            last_name="User",
            preferred_name="Admin"
        )
        self.client.login(email="admin@example.com", password="adminpass")
        url = reverse("admin_pending_societies")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_pending_societies.html")
        self.assertIn(pending_society, response.context["pending_socs"])

    def test_admin_confirm_society_decision_get(self):
        """
        Test that a GET request to admin_confirm_society_decision returns the confirmation page.
        """
        pending_society = Society.objects.create(
            name="Pending Confirm Society",
            description="Pending confirmation",
            society_type="academic",
            status="pending",
            visibility="Private",
            manager=self.user
        )
        admin = User.objects.create_superuser(
            email="admin2@example.com",
            password="adminpass",
            first_name="Admin2",
            last_name="User",
            preferred_name="Admin2"
        )
        self.client.login(email="admin2@example.com", password="adminpass")
        url = reverse("admin_confirm_society_decision", kwargs={"society_id": pending_society.id, "action": "approve"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that the confirmation template is used (assuming it is "admin_confirm_decision.html")
        self.assertTemplateUsed(response, "admin_confirm_decision.html")

    def test_view_all_members_superuser(self):
        """
        Test that view_all_members returns the member list for a superuser.
        """
        admin = User.objects.create_superuser(
            email="super@example.com",
            password="superpass",
            first_name="Super",
            last_name="User",
            preferred_name="Super"
        )
        self.client.login(email="super@example.com", password="superpass")
        # We assume there is a society with id=1 for this view (as per the code)
        Society.objects.create(
            name="All Members Society",
            description="All members",
            society_type="academic",
            status="approved",
            manager=self.user
        )
        url = reverse("view_all_members")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manage_society.html")

    def test_view_all_members_non_admin(self):
        """
        Test that view_all_members redirects non-admin users.
        """
        self.client.login(email="user@example.com", password="userpass")
        url = reverse("view_all_members")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_society_page_excludes_member_only_widgets_for_non_members(self):
        """
        Test that a widget with type "discussion" is excluded for users who are not members.
        """
        # Add a "discussion" widget to the society.
        Widget.objects.create(society=self.society, widget_type="discussion", position=0)
        url = reverse("society_page", args=[self.society.id])
        # Without login (non-member) the discussion widget should be excluded.
        response = self.client.get(url)
        widgets = response.context.get("widgets", [])
        widget_types = [w.widget_type for w in widgets]
        self.assertNotIn("discussion", widget_types)

    def test_leave_society_not_member(self):
        """
        Test that leave_society displays an error when the user is not a member.
        """
        self.client.login(email="user@example.com", password="userpass")
        url = reverse("leave_society", args=[self.society.id])
        response = self.client.post(url)
        # Should redirect back to society page with error message.
        self.assertEqual(response.status_code, 302)