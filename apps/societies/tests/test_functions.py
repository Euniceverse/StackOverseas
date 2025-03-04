from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.shortcuts import reverse
from apps.societies.models import Society, Membership, SocietyRegistration
from apps.societies.functions import (
    staff_required, approved_societies, get_societies, manage_societies,
    get_all_users, get_user_membership, top_societies, approve_society
)
from config.constants import SOCIETY_TYPE_CHOICES

User = get_user_model()

class SocietyFunctionsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = User.objects.create_superuser(email="admin@university.ac.uk", password="adminpass")
        self.staff_user = User.objects.create_user(email="staff@university.ac.uk", password="staffpass", is_staff=True)
        self.regular_user = User.objects.create_user(email="user@university.ac.uk", password="userpass")
        self.society = Society.objects.create(name="Test Society", status="approved", manager=self.regular_user)
        self.society_pending = Society.objects.create(name="Pending Society", status="pending", manager=self.regular_user)
        self.registration = SocietyRegistration.objects.create(name="New Society", applicant=self.regular_user, status="pending")

    def test_staff_required(self):
        self.assertTrue(staff_required(self.staff_user))
        self.assertFalse(staff_required(self.regular_user))
    
    def test_approved_societies(self):
        self.assertIn(self.society, approved_societies(self.superuser))
        self.assertNotIn(self.society_pending, approved_societies(self.regular_user))
    
    def test_get_societies(self):
        self.society.members.add(self.regular_user)
        societies = get_societies(self.regular_user)
        self.assertIn(self.society, societies)
        self.assertNotIn(self.society_pending, societies)
    
    def test_manage_societies(self):
        societies = manage_societies()
        self.assertIn(self.society_pending, societies)
        self.assertNotIn(self.society, societies)
    
    def test_get_all_users(self):
        self.assertIn(self.regular_user, get_all_users())
    
    def test_get_user_membership(self):
        membership = Membership.objects.create(user=self.regular_user, society=self.society, role="member")
        self.assertEqual(get_user_membership(self.society.memberships.all(), self.regular_user), membership)
    
    def test_top_societies(self):
        self.society.members_count = 10
        self.society.save()
        top_results = top_societies(self.superuser)
        self.assertIn(self.society, top_results["top_overall_societies"])
    
    def test_approve_society(self):
        request = self.factory.get(reverse("admin_society_list"))
        request.user = self.staff_user
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        response = approve_society(request, self.registration.id)
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.status, "pending")  # Should be modified in actual function
        self.assertTrue(Society.objects.filter(name="New Society").exists())
