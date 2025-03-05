from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.societies.models import (
    Society, 
    Membership, 
    MembershipRole, 
    MembershipStatus
)

User = get_user_model()

class MembershipModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='manager@university.ac.uk',
            first_name='Manager',
            last_name='User',
            preferred_name='Boss',
            password='password123'
        )
        self.society = Society.objects.create(
            name='Test Society',
            description='A test society',
            society_type='academic',
            manager=self.user,
            status='approved'
        )

    def test_membership_creation(self):
        """Ensure we can create a membership with default role/status."""
        membership = Membership.objects.create(
            society=self.society,
            user=self.user,
            role=MembershipRole.MEMBER,
            status=MembershipStatus.PENDING
        )
        self.assertEqual(membership.role, MembershipRole.MEMBER)
        self.assertEqual(membership.status, MembershipStatus.PENDING)

    def test_role_and_status_display(self):
        """Check that get_role_display and get_status_display produce correct strings."""
        membership = Membership.objects.create(
            society=self.society,
            user=self.user,
            role=MembershipRole.CO_MANAGER,
            status=MembershipStatus.APPROVED
        )
        self.assertEqual(membership.get_role_display(), 'Co-Manager')
        self.assertEqual(membership.get_status_display(), 'Approved')

class ManageSocietyViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Manager user
        self.manager_user = User.objects.create_user(
            email='manager@university.ac.uk',
            first_name='Manager',
            last_name='User',
            preferred_name='Boss',
            password='password123'
        )
        # Non-manager user
        self.normal_user = User.objects.create_user(
            email='member@university.ac.uk',
            first_name='John',
            last_name='Doe',
            preferred_name='JD',
            password='password123'
        )
        # Another user for co_manager
        self.co_manager_user = User.objects.create_user(
            email='co_manager@university.ac.uk',
            first_name='Co',
            last_name='Manager',
            preferred_name='CoBoss',
            password='password123'
        )

        # Society with manager=manager_user
        self.society = Society.objects.create(
            name='Test Society',
            description='A test society',
            society_type='academic',
            manager=self.manager_user,
            status='approved'
        )

        # Some existing memberships
        Membership.objects.create(
            society=self.society,
            user=self.normal_user,
            role=MembershipRole.MEMBER,
            status=MembershipStatus.PENDING
        )
        # Mark co_manager_user as a co-manager
        Membership.objects.create(
            society=self.society,
            user=self.co_manager_user,
            role=MembershipRole.CO_MANAGER,
            status=MembershipStatus.APPROVED
        )

        self.manage_url = reverse('manage_society', args=[self.society.id])

    def test_manager_can_access_manage_page(self):
        """Society manager can see the manage page."""
        self.client.login(email='manager@university.ac.uk', password='password123')
        response = self.client.get(self.manage_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Manage Society: Test Society')
        # Should see normal_user membership and co_manager membership
        self.assertContains(response, 'member@university.ac.uk')
        self.assertContains(response, 'co_manager@university.ac.uk')

    def test_co_manager_can_access_manage_page(self):
        """A user with role=CO_MANAGER and status=approved can also see the page."""
        self.client.login(email='co_manager@university.ac.uk', password='password123')
        response = self.client.get(self.manage_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Manage Society: Test Society')

    def test_normal_user_cannot_access_manage_page(self):
        """A normal member who is not manager/co_manager cannot access it."""
        self.client.login(email='member@university.ac.uk', password='password123')
        response = self.client.get(self.manage_url)
        # either redirect or show an error (in the sample code, we redirect with a message).
        self.assertNotEqual(response.status_code, 200)

        self.assertIn(response.status_code, [302, 403])

class UpdateMembershipViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Manager user
        self.manager_user = User.objects.create_user(
            email='manager@uni.ac.uk',
            first_name='Boss',
            last_name='Man',
            preferred_name='Bossy',
            password='managerpass'
        )
        # Another user
        self.other_user = User.objects.create_user(
            email='other@uni.ac.uk',
            first_name='Other',
            last_name='User',
            preferred_name='OU',
            password='otherpass'
        )
        # Society
        self.society = Society.objects.create(
            name='Another Society',
            description='Yet another test society',
            society_type='academic',
            manager=self.manager_user,
            status='approved'
        )
        # Membership for other_user, initially pending
        self.membership = Membership.objects.create(
            society=self.society,
            user=self.other_user,
            role=MembershipRole.MEMBER,
            status=MembershipStatus.PENDING
        )
        self.update_url = reverse('update_membership', args=[self.society.id, self.other_user.id])

    def test_approve_pending_member(self):
        """Manager can approve a pending membership."""
        self.client.login(email='manager@uni.ac.uk', password='managerpass')
        response = self.client.post(self.update_url, {
            'action': 'approve'
        }, follow=True)
        self.assertEqual(response.status_code, 200) # 302 if redirect
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.status, MembershipStatus.APPROVED)

    def test_remove_member(self):
        """Manager can remove a membership altogether."""
        self.client.login(email='manager@uni.ac.uk', password='managerpass')
        response = self.client.post(self.update_url, {
            'action': 'remove'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        # membership should no longer exist
        with self.assertRaises(Membership.DoesNotExist):
            self.membership.refresh_from_db()

    def test_promote_to_co_manager(self):
        """Manager can promote a member to co_manager."""
        self.client.login(email='manager@uni.ac.uk', password='managerpass')
        response = self.client.post(self.update_url, {
            'action': 'promote_co_manager'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.role, MembershipRole.CO_MANAGER)
        self.assertEqual(self.membership.status, MembershipStatus.APPROVED)

    def test_unauthorized_user_cannot_update(self):
        """A normal user cannot update membership of another user."""
        self.client.login(email='other@uni.ac.uk', password='otherpass')
        # 'other_user' tries to update membership (themselves?) but they're not manager or co_manager
        response = self.client.post(self.update_url, {'action': 'approve'})
        # Expect a redirect or forbidden
        self.assertNotEqual(response.status_code, 200)
        # membership should remain unchanged
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.status, MembershipStatus.PENDING)