from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.shortcuts import reverse
from django.utils import timezone
from apps.societies.models import Society, Membership, SocietyRegistration
from apps.users.models import CustomUser
from apps.societies.functions import (
    staff_required, approved_societies, get_societies, manage_societies,
    get_all_users, get_user_membership, top_societies, approve_society
)

class FunctionsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = CustomUser.objects.create_superuser(
            email="admin@university.ac.uk",
            first_name="Admin",
            last_name="User",
            preferred_name="AdminUser",
            password="pass"
        )
        
        self.staff_user = CustomUser.objects.create_user(
            email="staff@university.ac.uk",
            first_name="Staff",
            last_name="User",
            preferred_name="StaffUser",
            password="pass",
        )
        
        self.staff_user.is_staff = True
        self.staff_user.save()

        self.regular_user = CustomUser.objects.create_user(
            email="user@university.ac.uk",
            first_name="Regular",
            last_name="User",
            preferred_name="RegularUser",
            password="pass"
        )
        
        self.society = Society.objects.create(
            name="Test Society",
            status="approved",
            members_count=10,
            manager=self.staff_user,
            visibility="Public"
        )
        
        self.pending_registration = SocietyRegistration.objects.create(
            name="Pending Society",
            description="A test society",
            society_type="type1",
            applicant=self.regular_user,
            status="pending"
        )
        
        self.membership = Membership.objects.create(
            user=self.regular_user,
            society=self.society
        )
    
    def test_staff_required(self):
        self.assertTrue(staff_required(self.staff_user))
        self.assertFalse(staff_required(self.regular_user))
        self.assertTrue(staff_required(self.superuser))
    
    def test_approved_societies(self):
        self.assertIn(self.society, approved_societies(self.superuser))
        self.assertIn(self.society, approved_societies(self.regular_user))
        self.assertEqual(len(approved_societies(self.superuser)), 1)
    
    def test_get_societies_valid_user(self):
        self.assertIn(self.society, get_societies(self.regular_user))
    
    def test_get_societies_invalid_user(self):
        fake_user = CustomUser(id=999)  # Non-existent user
        self.assertEqual(list(get_societies(fake_user)), list(approved_societies(fake_user)))
    
    def test_manage_societies_regular_user(self):
        result = manage_societies(self.staff_user) 
        self.assertEqual(list(result["registrations"]), [])
        self.assertEqual(list(result["societies"]), [])

    def test_manage_societies_invalid_user(self):
        fake_user = CustomUser(id=999)  # Non-existent user instance.
        result = manage_societies(fake_user)
        self.assertEqual(list(result["registrations"]), [])
        self.assertEqual(list(result["societies"]), [])

    def test_manage_societies_admin_only(self):
        result = manage_societies(self.superuser)
        expected_registrations = list(SocietyRegistration.objects.filter(status="pending"))
        expected_societies = list(Society.objects.filter(status__in=['pending', 'request_delete']))
        self.assertEqual(list(result["registrations"]), expected_registrations)
        self.assertEqual(list(result["societies"]), expected_societies)

    def test_get_all_users_with_memberships(self):
        self.assertIn(self.regular_user, get_all_users())
    
    def test_get_all_users_no_memberships(self):
        new_user = CustomUser.objects.create_user(
            email="new_user@university.ac.uk",
            first_name="New",
            last_name="User",
            preferred_name="NewUser",
            password="pass"
        )
        self.assertNotIn(new_user, get_all_users())
    
    def test_get_user_membership_valid(self):
        memberships = Membership.objects.all()
        self.assertEqual(get_user_membership(memberships, self.regular_user), self.membership)
    
    def test_get_user_membership_invalid(self):
        memberships = Membership.objects.all()
        new_user = CustomUser.objects.create_user(
            email="new_user@university.ac.uk",
            first_name="New",
            last_name="User",
            preferred_name="NewUser",
            password="pass"
        )
        self.assertIsNone(get_user_membership(memberships, new_user))
    
    def test_top_societies(self):
        top = top_societies(self.superuser)
        self.assertIn("top_overall_societies", top)
        self.assertIn("top_societies_per_type", top)
        self.assertIn(self.society, top["top_overall_societies"])
    
    def test_top_societies_no_societies(self):
        Society.objects.all().delete()
        top = top_societies(self.superuser)
        self.assertEqual(len(top["top_overall_societies"]), 0)
    
    def test_approve_society_success(self):
        request = self.factory.get(reverse("admin_pending_societies"))
        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(request)
        request.session.save()
        request._messages = FallbackStorage(request)
        request.user = self.staff_user
        
        response = approve_society(request, self.pending_registration.id)
        self.assertEqual(Society.objects.filter(name="Pending Society").count(), 1)
    
    def test_approve_society_non_staff(self):
        request = self.factory.get(reverse("admin_pending_societies"))
        request.user = self.regular_user
        response = approve_society(request, self.pending_registration.id)
        self.assertEqual(Society.objects.filter(name="Pending Society").count(), 0)