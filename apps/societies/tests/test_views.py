from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.models import User
from unittest.mock import patch
import json

from apps.societies.models import Society, SocietyRegistration, Membership, MembershipRole, MembershipStatus, MembershipApplication, Widget
from apps.news.models import News
from apps.societies.functions import get_societies, manage_societies, get_all_users

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
        self.client.login(email='test@example.ac.uk', password='password123')

        self.society = Society.objects.create(
            name="Tech Club",
            description="A club for tech enthusiasts",
            society_type="academic",
            status = "pending",
            manager=self.user)

    def test_societies_page_status_code(self):
        """Test if /societies/ page loads correctly"""
        response = self.client.get(reverse('societiespage'))
        self.assertEqual(response.status_code, 200)  # Should return HTTP 200 OK

    def test_fetch_societies_list(self):
        response = self.client.get(reverse('society-list'))
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
        response = self.client.post(reverse('society-create'), {
            "name": "Art Club",
            "description": "A club for artists",
            "society_type": "arts"
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Society.objects.filter(name="Art Club").exists())

    def test_update_society(self):
        response = self.client.post(reverse('society-update', args=[self.society.id]), {
            "name": "Updated Tech Club",
        })
        self.society.refresh_from_db()
        self.assertEqual(self.society.name, "Updated Tech Club")

    def test_delete_society(self):
        response = self.client.post(reverse('society-delete', args=[self.society.id]))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Society.objects.filter(id=self.society.id).exists())

    def test_join_society(self):
        response = self.client.post(reverse('society-join', args=[self.society.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user, self.society.members.all())


    def test_update_membership_approve(self):
        """Test approving a membership."""
        other_user = get_user_model().objects.create_user(
            email='member@example.ac.uk', password='password123')
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
            email='member@example.ac.uk', password='password123')
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
            email='co_manager@example.ac.uk', password='password123')
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
            email='editor@example.ac.uk', password='password123')
        membership = Membership.objects.create(
            society=self.society, user=other_user, role=MembershipRole.MEMBER, status=MembershipStatus.APPROVED)
        
        response = self.client.post(reverse('update_membership', args=[self.society.id, other_user.id]), {
            'action': 'promote_editor'
        })
        
        membership.refresh_from_db()
        self.assertEqual(membership.role, MembershipRole.EDITOR)
        self.assertEqual(membership.status, MembershipStatus.APPROVED)
        self.assertRedirects(response, reverse('manage_society', args=[self.society.id]))

    def test_return_redirect_on_invalid_request(self):
        """Test that non-POST requests redirect properly."""
        response = self.client.get(reverse('update_membership', args=[self.society.id, self.user.id]))
        self.assertRedirects(response, reverse('manage_society', args=[self.society.id]))


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
        self.assertEqual(len(response.context["societies"]), 0)
    
    @patch("apps.news.models.News.objects.filter")
    def test_my_societies_news_list(self, mock_news_filter):
        Membership.objects.create(user=self.user, society=self.society)
        
        mock_news_filter.return_value.order_by.return_value[:10] = [News(title="Test News")]
        response = self.client.get(reverse("my_societies"))
        self.assertIn("news_list", response.context)
        self.assertEqual(len(response.context["news_list"]), 1)
        self.assertEqual(response.context["news_list"][0].title, "Test News")




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

class ApplicationManagementTest(TestCase):
    def setUp(self):
        """Set up a test user and client."""
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email="test@university.ac.uk",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="Password123"
        )
        self.manager = get_user_model().objects.create_user(
            email="manager@university.ac.uk",
            password="ManagerPass"
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
        self.assertTemplateUsed(response, "societies/view_applications.html")
        self.assertIn("applications", response.context)
    
    def test_view_applications_no_permission(self):
        self.client.login(email="test@university.ac.uk", password="Password123")
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
        self.user = User.objects.create_user(username="testuser", password="password123")

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
        other_user = User.objects.create_user(username="otheruser", password="password123")
        self.client.login(username="otheruser", password="password123")
        response = self.client.post(self.url_small)
        self.small_society.refresh_from_db()
        self.assertEqual(self.small_society.status, "approved") 
        self.assertEqual(response.status_code, 403)


class ManageSocietiesAndMembersTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='test@example.ac.uk',
            password='password123',
            first_name='Test',
            last_name='User',
            preferred_name='Tester'
        )
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.ac.uk',
            password='adminpass'
        )
        self.client.login(email='test@example.ac.uk', password='password123')

        self.society = Society.objects.create(
            name="Tech Club",
            description="A club for tech enthusiasts",
            society_type="academic",
            status="pending",
            manager=self.user
        )
    
    def test_view_manage_societies_authenticated(self):
        response = self.client.get(reverse("view_manage_societies"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "societies.html")
        self.assertIn("societies", response.context)
    
    @patch("apps.news.models.News.objects.filter")
    def test_view_manage_societies_with_news(self, mock_news_filter):
        mock_news_filter.return_value.order_by.return_value[:10] = [News(title="Tech News")]
        response = self.client.get(reverse("view_manage_societies"))
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
            email='test@example.ac.uk',
            password='password123',
            first_name='Test',
            last_name='User',
            preferred_name='Tester'
        )
        self.manager = get_user_model().objects.create_user(
            email='manager@example.ac.uk',
            password='managerpass'
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
        self.client.login(email='test@example.ac.uk', password='password123')
        response = self.client.post(reverse("update_membership", args=[self.society.id, self.user.id]), {"action": "approve"})
        self.assertEqual(response.status_code, 302)
    
    def test_society_detail(self):
        response = self.client.get(reverse("society_detail", args=[self.society.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "society_detail.html")
        self.assertIn("society", response.context)
    
    def test_join_society_already_member(self):
        self.membership.status = MembershipStatus.APPROVED
        self.membership.save()
        response = self.client.get(reverse("join_society", args=[self.society.id]))
        self.assertRedirects(response, reverse("society_detail", args=[self.society.id]))
    
    def test_join_society_new_application(self):
        self.client.login(email='test@example.ac.uk', password='password123')
        response = self.client.post(reverse("join_society", args=[self.society.id]), {})
        self.assertRedirects(response, reverse("society_detail", args=[self.society.id]))



class SocietyDeletionAndWidgetsTest(TestCase):
    def setUp(self):
        """Set up a test user and client."""
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email="test@university.ac.uk",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="Password123"
        )
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@university.ac.uk",
            password="AdminPass"
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
        self.client.login(email="test@university.ac.uk", password="Password123")
    
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
        another_user = get_user_model().objects.create_user(email="another@uni.ac.uk", password="pass")
        self.client.login(email="another@uni.ac.uk", password="pass")
        response = self.client.get(reverse("society_admin_view", args=[self.society.id]))
        self.assertEqual(response.status_code, 302)  # Redirect due to permission error
    
    def test_remove_widget_success(self):
        response = self.client.post(reverse("remove_widget", args=[self.society.id, self.widget.id]))
        self.assertFalse(Widget.objects.filter(id=self.widget.id).exists())
        self.assertRedirects(response, reverse("society_admin_view", args=[self.society.id]))
    
    def test_remove_widget_no_permission(self):
        another_user = get_user_model().objects.create_user(email="another@uni.ac.uk", password="pass")
        self.client.login(email="another@uni.ac.uk", password="pass")
        response = self.client.post(reverse("remove_widget", args=[self.society.id, self.widget.id]))
        self.assertEqual(response.status_code, 302)  # Redirect due to permission error
    
    def test_society_page_view(self):
        response = self.client.get(reverse("society_page", args=[self.society.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "societies/society_page.html")
    
    def test_update_widget_order_success(self):
        self.client.post(reverse("update_widget_order", args=[self.society.id]), data=json.dumps({"widget_order": [self.widget.id]}), content_type="application/json")
        self.widget.refresh_from_db()
        self.assertEqual(self.widget.position, 0)