from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template import Context, Template
from django.utils import timezone

from apps.societies.models import (
    Society, Membership, MembershipStatus, MembershipRole,
    SocietyRequirement, RequirementType, SocietyQuestion,
    MembershipApplication
)

User = get_user_model()

class TestTemplateFilter(TestCase):
    """
    Test the custom 'get_user_membership' template filter.
    """
    def test_get_user_membership_filter(self):
        # Create a user, society, membership
        user = User.objects.create_user(
            email='filteruser@uni.ac.uk',
            password='testpass',
            first_name='Filter',
            last_name='User',
            preferred_name='Filter'
        )
        soc = Society.objects.create(
            name='Filter Test Society',
            description='Filter test',
            manager=user,
            status='approved',
            society_type='academic'
        )
        mem = Membership.objects.create(
            society=soc, user=user, role=MembershipRole.MEMBER, status=MembershipStatus.APPROVED
        )

        # Minimal test of the template filter
        template_str = """
            {% with membership_list=society.society_memberships.all %}
                {% with mymem=membership_list.0 %}
                    Role: {{ mymem.role }} Status: {{ mymem.status }}
                {% endwith %}
            {% endwith %}
        """
        t = Template(template_str)
        c = Context({"society": soc, "user": user})
        rendered = t.render(c)

        self.assertIn("Role: member Status: approved", rendered)

class NoRequirementJoinTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='noreq@uni.ac.uk',
            password='pass123',
            first_name='No',
            last_name='Requirement',
            preferred_name='None'
        )
        self.society = Society.objects.create(
            name='NoReq Society',
            description='No requirements at all',
            manager=self.user,  
            status='approved',
            society_type='academic'
        )
        # By default, there's no SocietyRequirement => treat as none
        self.join_url = reverse('join_society', args=[self.society.id])

    def test_auto_join(self):
        self.client.login(email='noreq@uni.ac.uk', password='pass123')
        response = self.client.post(self.join_url)
        # Should redirect to society_page
        detail_url = reverse('society_page', args=[self.society.id])
        self.assertRedirects(response, detail_url)
        membership = Membership.objects.get(society=self.society, user=self.user)
        self.assertEqual(membership.status, 'approved')


class QuizRequirementJoinTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create user, manager, society, requirement=quiz
        self.quiz_taker = User.objects.create_user(
            email='quiz@uni.ac.uk',
            password='quizpass',
            first_name='Quiz',
            last_name='Guy',
            preferred_name='Quizzy'
        )
        self.quiz_manager = User.objects.create_user(
            email='quizmgr@uni.ac.uk',
            password='mgrpass',
            first_name='Quiz',
            last_name='Manager',
            preferred_name='Quizzed'
        )
        self.quiz_soc = Society.objects.create(
            name='Quiz Society',
            description='Must pass quiz to join',
            manager=self.quiz_manager,
            status='approved',
            society_type='academic'
        )
        self.req = SocietyRequirement.objects.create(
            society=self.quiz_soc,
            requirement_type=RequirementType.QUIZ,
            threshold=2
        )
        # Three questions
        self.q1 = SocietyQuestion.objects.create(
            society_requirement=self.req,
            question_text='Is Python a snake or language? (Yes=Language, No=Snake? )',
            correct_answer=True  # "Yes"
        )
        self.q2 = SocietyQuestion.objects.create(
            society_requirement=self.req,
            question_text='Is 2+2=4? (Yes=4, No=5?)',
            correct_answer=True
        )
        self.q3 = SocietyQuestion.objects.create(
            society_requirement=self.req,
            question_text='Is Earth flat? (Yes=Flat, No=Round?)',
            correct_answer=False
        )
        self.join_url = reverse('join_society', args=[self.quiz_soc.id])

    def test_pass_quiz(self):
        self.client.login(email='quiz@uni.ac.uk', password='quizpass')
        data = {
            f'question_{self.q1.id}': 'yes',  # correct
            f'question_{self.q2.id}': 'yes',  # correct
            f'question_{self.q3.id}': 'yes',  # incorrect (since correct_answer=False)
        }
        response = self.client.post(self.join_url, data)
        self.assertRedirects(response, reverse('society_page', args=[self.quiz_soc.id]))
        # Should be approved, because 2 out of 3 are correct, threshold=2
        mem = Membership.objects.get(society=self.quiz_soc, user=self.quiz_taker)
        self.assertEqual(mem.status, MembershipStatus.APPROVED)

    def test_fail_quiz(self):
        self.client.login(email='quiz@uni.ac.uk', password='quizpass')
        data = {
            f'question_{self.q1.id}': 'no',   # incorrect
            f'question_{self.q2.id}': 'no',   # incorrect
            f'question_{self.q3.id}': 'yes',  # incorrect
        }
        response = self.client.post(self.join_url, data)
        self.assertRedirects(response, reverse('society_page', args=[self.quiz_soc.id]))
        # membership should not exist or be removed
        self.assertFalse(Membership.objects.filter(society=self.quiz_soc, user=self.quiz_taker).exists())
        # Also check the application is marked is_rejected
        app = MembershipApplication.objects.filter(user=self.quiz_taker, society=self.quiz_soc).first()
        self.assertIsNotNone(app)
        self.assertTrue(app.is_rejected)


class ManualRequirementJoinTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='manual@uni.ac.uk',
            password='manualpass',
            first_name='Manual',
            last_name='Requirement',
            preferred_name='Manual'
        )
        self.manager = User.objects.create_user(
            email='manager@uni.ac.uk',
            password='managerpass',
            first_name='Manager',
            last_name='Test',
            preferred_name='Manage'
        )
        self.soc = Society.objects.create(
            name='Manual Society',
            description='Essay or PDF, manager decides',
            manager=self.manager,
            status='approved',
            society_type='academic'
        )
        from apps.societies.models import SocietyRequirement
        self.req = SocietyRequirement.objects.create(
            society=self.soc,
            requirement_type=RequirementType.MANUAL,
            requires_essay=True, 
            requires_portfolio=True  # require a PDF
        )
        self.join_url = reverse('join_society', args=[self.soc.id])

    def test_submit_essay_and_pdf(self):
        """
        Submitting the manual application => membership is pending
        manager must later approve or reject.
        """
        self.client.login(email='manual@uni.ac.uk', password='manualpass')
        pdf_file = SimpleUploadedFile("test.pdf", b"fake-pdf-data", content_type="application/pdf")
        data = {
            'essay_text': 'My essay about joining the society',
            'portfolio_file': pdf_file
        }
        response = self.client.post(self.join_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        mem = Membership.objects.get(society=self.soc, user=self.user)
        self.assertEqual(mem.status, MembershipStatus.PENDING)
        app = MembershipApplication.objects.get(society=self.soc, user=self.user)
        self.assertFalse(app.is_approved)
        self.assertFalse(app.is_rejected)
        self.assertIn('fake-pdf-data', app.portfolio_file.read().decode('utf-8', 'ignore'))

    def test_missing_essay(self):
        """
        The form requires essay & PDF because SocietyRequirement says so.
        If we omit essay_text => validation error.
        """
        self.client.login(email='manual@uni.ac.uk', password='manualpass')
        pdf_file = SimpleUploadedFile("test.pdf", b"fake", content_type="application/pdf")
        data = {
            # 'essay_text': missing
            'portfolio_file': pdf_file
        }
        response = self.client.post(self.join_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('An essay is required.', response.content.decode())
        # membership won't exist
        self.assertFalse(Membership.objects.filter(society=self.soc, user=self.user).exists())


class ManagerApplicationDecisionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = User.objects.create_user(
            email='boss@uni.ac.uk',
            password='bosspass',
            first_name='Boss',
            last_name='Apps',
            preferred_name='Boss'
        )
        self.applicant = User.objects.create_user(
            email='applicant@uni.ac.uk',
            password='apppass',
            first_name='Applicant',
            last_name='Decision',
            preferred_name='App'
        )
        self.soc = Society.objects.create(
            name='ManualSoc',
            manager=self.manager,
            description='Manual approval society',
            status='approved',
            society_type='academic'
        )
        from apps.societies.models import SocietyRequirement
        self.req = SocietyRequirement.objects.create(
            society=self.soc,
            requirement_type=RequirementType.MANUAL,
            requires_essay=True
        )
        # The applicant has a pending membership
        self.app = MembershipApplication.objects.create(
            user=self.applicant,
            society=self.soc,
            essay_text='I love this society!',
            is_approved=False,
            is_rejected=False
        )
        # Also a Membership record with status=pending
        self.membership = Membership.objects.create(
            society=self.soc,
            user=self.applicant,
            role='member',
            status='pending'
        )
        self.view_apps_url = reverse('view_applications', args=[self.soc.id])
        self.decide_url_approve = reverse('decide_application', args=[self.soc.id, self.app.id, 'approve'])
        self.decide_url_reject = reverse('decide_application', args=[self.soc.id, self.app.id, 'reject'])

    def test_only_manager_can_view_applications(self):
        # Log in as the applicant => not manager => no access
        self.client.login(email='applicant@uni.ac.uk', password='apppass')
        response = self.client.get(self.view_apps_url)
        self.assertNotEqual(response.status_code, 200)

        # Log in as manager => can see
        self.client.login(email='boss@uni.ac.uk', password='bosspass')
        response = self.client.get(self.view_apps_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'I love this society!')  # the essay

    def test_approve_application(self):
        self.client.login(email='boss@uni.ac.uk', password='bosspass')
        response = self.client.get(self.decide_url_approve)
        # Typically we do a redirect back to the applications page
        self.assertRedirects(response, self.view_apps_url)
        self.app.refresh_from_db()
        self.assertTrue(self.app.is_approved)
        mem = Membership.objects.get(id=self.membership.id)
        self.assertEqual(mem.status, MembershipStatus.APPROVED)

    def test_reject_application(self):
        self.client.login(email='boss@uni.ac.uk', password='bosspass')
        response = self.client.get(self.decide_url_reject)
        self.assertRedirects(response, self.view_apps_url)
        self.app.refresh_from_db()
        self.assertTrue(self.app.is_rejected)
        # membership should be removed
        self.assertFalse(Membership.objects.filter(id=self.membership.id).exists())


class ManageButtonVisibilityTest(TestCase):
   
    def setUp(self):
        self.client = Client()
        self.user_manager = User.objects.create_user(
            email='mgr@uni.ac.uk', 
            password='mgrpass',
            first_name='Manager',
            last_name='Client',
            preferred_name='Mgr'
        )
        self.user_normal = User.objects.create_user(
            email='norm@uni.ac.uk', 
            password='normpass',
            first_name='Normal',
            last_name='User',
            preferred_name='Norm'
        )
        self.user_editor = User.objects.create_user(
            email='editor@uni.ac.uk', 
            password='editorpass',
            first_name='Editor',
            last_name='Tester',
            preferred_name='Edit'
        )
        self.soc = Society.objects.create(
            name='VisibilitySoc',
            manager=self.user_manager,
            status='approved',
            society_type='academic'
        )
        self.detail_url = reverse('society_page', args=[self.soc.id])

    def test_manager_can_see_button(self):
        """
        If the user is the manager with status=approved => show manage button.
        """
        # The manager might not have an actual membership record, 
        # but let's create it for consistency.
        Membership.objects.create(
            society=self.soc,
            user=self.user_manager,
            role=MembershipRole.MANAGER,
            status=MembershipStatus.APPROVED
        )

        self.client.login(email='mgr@uni.ac.uk', password='mgrpass')
        response = self.client.get(self.detail_url)
        self.assertContains(response, 'Manage Members')

    def test_editor_sees_button(self):
        Membership.objects.create(
            society=self.soc,
            user=self.user_editor,
            role=MembershipRole.EDITOR,
            status=MembershipStatus.APPROVED
        )
        self.client.login(email='editor@uni.ac.uk', password='editorpass')
        response = self.client.get(self.detail_url)
        self.assertContains(response, 'Manage Members')

    def test_pending_editor_cannot_see_button(self):
        """
        If role=editor but status is pending => do not show Manage button.
        """
        Membership.objects.create(
            society=self.soc,
            user=self.user_editor,
            role=MembershipRole.EDITOR,
            status=MembershipStatus.PENDING
        )
        self.client.login(email='editor@uni.ac.uk', password='editorpass')
        response = self.client.get(self.detail_url)
        self.assertContains(response, 'Manage Members')

    def test_normal_member_cannot_see_button(self):
        """
        role=member => no manage button
        """
        Membership.objects.create(
            society=self.soc,
            user=self.user_normal,
            role=MembershipRole.MEMBER,
            status=MembershipStatus.APPROVED
        )
        self.client.login(email='norm@uni.ac.uk', password='normpass')
        response = self.client.get(self.detail_url)
        self.assertNotContains(response, 'Manage This Society')


User = get_user_model()

class JoinSocietyTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@university.ac.uk',
            password='password123',
            first_name='User',
            last_name='Join',
            preferred_name='User'
        )
        self.society = Society.objects.create(
            name='Test Society',
            description='A test society',
            society_type='academic',
            status='approved',
            manager=self.user
        )

    def test_user_can_request_to_join_society(self):
        self.client.login(email='user@university.ac.uk', password='password123')
        response = self.client.post(reverse('society-join', args=[self.society.id]))
        detail_url = reverse('society_page', args=[self.society.id])
        self.assertRedirects(response, detail_url)
        self.assertTrue(Membership.objects.filter(user=self.user, society=self.society).exists())

    def test_user_cannot_join_twice(self):
        Membership.objects.create(user=self.user, society=self.society, status=MembershipStatus.PENDING)
        self.client.login(email=self.user.email, password='password123')
        response = self.client.post(reverse('society-join', args=[self.society.id]))
        detail_url = reverse('society_page', args=[self.society.id])
        self.assertRedirects(response, detail_url)
        memberships = Membership.objects.filter(user=self.user, society=self.society)
        self.assertEqual(memberships.count(), 1)  # Ensure only one request exists

    def test_admin_can_approve_join_request(self):
        membership = Membership.objects.create(user=self.user, society=self.society, status=MembershipStatus.PENDING)
        self.client.login(email=self.user.email, password='password123')
        response = self.client.post(
            reverse('update_membership', args=[membership.society.id, membership.user.id]),
            {'action': 'approve'}
        )
        membership.refresh_from_db()
        self.assertEqual(membership.status, MembershipStatus.APPROVED)

    def test_unauthorized_user_cannot_approve_membership(self):
        membership = Membership.objects.create(user=self.user, society=self.society, status=MembershipStatus.PENDING)
        response = self.client.post(
            reverse('update_membership', args=[membership.society.id, membership.user.id]),
            {'action': 'approve'}
        )
        self.assertNotEqual(response.status_code, 200)  # Should be forbidden