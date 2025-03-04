# societies/tests/test_admin_approval.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import (
    Society, 
    Membership, 
    MembershipRole, 
    MembershipStatus
)

User = get_user_model()

class AdminApprovalTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Regular user
        self.regular_user = User.objects.create_user(
            email="user@university.ac.uk",
            first_name="Regular",
            last_name="User",
            preferred_name="RegUser",
            password="password123"
        )

        # Staff/ admin user
        self.admin_user = User.objects.create_superuser(
            email="admin@university.ac.uk",
            first_name="Admin",
            last_name="User",
            preferred_name="AdminUser",
            password="adminpass"
        )

        # Pending society
        self.pending_society = Society.objects.create(
            name="Pending Club",
            description="Test Pending Society",
            society_type="academic",
            manager=self.regular_user,  # manager doesn't have to be staff
            status="pending"
        )

        self.pending_url = reverse('admin_pending_societies')
        self.approve_url = reverse(
            'admin_confirm_society_decision',
            kwargs={'society_id': self.pending_society.id, 'action': 'approve'}
        )
        self.reject_url = reverse(
            'admin_confirm_society_decision',
            kwargs={'society_id': self.pending_society.id, 'action': 'reject'}
        )

    def test_non_staff_cannot_access_admin_view(self):
        """A non-admin user should get a 302 redirect when trying to view pending societies."""
        self.client.login(email="user@university.ac.uk", password="password123")
        response = self.client.get(self.pending_url)
        self.assertNotEqual(response.status_code, 200)  # Expect redirect or forbidden

    def test_admin_can_view_pending_societies(self):
        """An admin user can see the pending societies page."""
        self.client.login(email="admin@university.ac.uk", password="adminpass")
        response = self.client.get(self.pending_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending Club")

    def test_approve_society_flow(self):
        """Admin can approve a pending society -> status changes to 'approved'."""
        self.client.login(email="admin@university.ac.uk", password="adminpass")
  
        response = self.client.get(self.approve_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure you want to proceed?")

        response = self.client.post(self.approve_url, {'confirm': True})
        self.assertEqual(response.status_code, 302)  # redirects back to pending page

        # refresh from DB
        self.pending_society.refresh_from_db()
        self.assertEqual(self.pending_society.status, 'approved')


    def test_reject_society_flow(self):
        """Admin can reject a pending society -> it is discarded or set to 'rejected'."""
        self.client.login(email="admin@university.ac.uk", password="adminpass")

        response = self.client.get(self.reject_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure you want to proceed?")

        response = self.client.post(self.reject_url, {'confirm': True})
        self.assertEqual(response.status_code, 302)

        # If you delete on reject:
        self.assertFalse(Society.objects.filter(id=self.pending_society.id).exists())

    def test_cancel_action(self):
        """Clicking 'cancel' on the confirm page returns to the pending page without changes."""
        self.client.login(email="admin@university.ac.uk", password="adminpass")
        response = self.client.post(self.approve_url, {'cancel': True})
        self.assertEqual(response.status_code, 302)
        # society should remain pending
        self.pending_society.refresh_from_db()
        self.assertEqual(self.pending_society.status, 'pending')

    def test_membership_approval(self):
        membership = Membership.objects.create(
            society=self.society,
            user=self.user,
            status=MembershipStatus.PENDING
        )
        membership.status = MembershipStatus.APPROVED
        membership.save()
        self.assertEqual(membership.status, MembershipStatus.APPROVED)

    def test_unauthorized_membership_approval(self):
        membership = Membership.objects.create(
            society=self.society,
            user=self.user,
            status=MembershipStatus.PENDING
        )
        response = self.client.post(reverse('approve-membership', args=[membership.id]))
        self.assertNotEqual(response.status_code, 200)  # Expect failure without admin rights