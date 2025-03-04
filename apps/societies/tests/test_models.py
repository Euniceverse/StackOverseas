from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.societies.models import Society, Membership, SocietyRequirement, Question, MembershipApplication, SocietyRegistration, ExtraForm, Widget
from django.db.utils import IntegrityError
from django.apps import apps

class SocietyModelTest(TestCase):

    def setUp(self):
        # Create a test user with CustomUser model
        self.user = get_user_model().objects.create_user(
            email='test@example.ac.uk',
            password='password123',
            first_name='Test',
            last_name='User',
            preferred_name='Tester'
        )

        self.society = Society.objects.create(
            name="Tech Club",
            description="A society for tech enthusiasts.",
            society_type="Technology",
            status="pending",
            membership_request_required=True,
            manager=self.user
        )

    def test_society_creation(self):
        self.assertEqual(self.society.name, "Tech Club")
        self.assertEqual(self.society.status, "pending")
        self.assertEqual(self.society.manager.email, "test@example.ac.uk")  # Changed from username to email
        self.assertTrue(self.society.membership_request_required)

    def test_is_customisable(self):
        self.assertFalse(self.society.is_customisable())  # the default is "pending"

        self.society.status = "approved"
        self.society.save()
        self.assertTrue(self.society.is_customisable())

    def test_default_values(self):
        new_society = Society.objects.create(
            name="Music Club",
            description="A society for music lovers.",
            society_type="Cultural",
            manager=self.user
        )
        self.assertEqual(new_society.status, "pending")
        self.assertFalse(new_society.membership_request_required)

    def test_unique_society_name(self):
        with self.assertRaises(Exception):
            Society.objects.create(
                name="Tech Club",  # same name as before
                description="Another tech club",
                society_type="Technology",
                manager=self.user
            )

    def test_default_status(self):
        new_society = Society.objects.create(
            name="Art Club",
            description="A society for artists.",
            society_type="Art"
        )
        self.assertEqual(new_society.status, "pending")

    def test_add_member_to_society(self):
        self.society.members.add(self.user)
        self.assertIn(self.user, self.society.members.all())

    def test_update_society(self):
        self.society.name = "Updated Tech Club"
        self.society.save()
        updated_society = Society.objects.get(id=self.society.id)
        self.assertEqual(updated_society.name, "Updated Tech Club")

    def test_delete_society(self):
        society_id = self.society.id
        self.society.delete()
        with self.assertRaises(Society.DoesNotExist):
            Society.objects.get(id=society_id)

    def test_get_events(self):
        Event = apps.get_model("events", "Event")
        event = Event.objects.create(name="Tech Meetup", host=self.society)
        self.assertIn(event, self.society.get_events())

    def test_membership_str(self):
        membership = Membership.objects.create(user=self.user, society=self.society, role="Member")
        self.assertEqual(str(membership), f"{self.user.email} - {self.society.name} ({membership.role})")

    def test_society_requirement_str(self):
        requirement = SocietyRequirement.objects.create(society=self.society, requirement_type="quiz")
        self.assertEqual(str(requirement), f"Requirement for {self.society.name} ({requirement.get_requirement_type_display()})")

    def test_question_str(self):
        question = Question.objects.create(requirement=SocietyRequirement.objects.create(society=self.society, requirement_type="quiz"), question_text="Sample Question", correct_answer=True)
        self.assertEqual(str(question), f"Q: {question.question_text} (Correct={question.correct_answer})")

    def test_membership_application_str(self):
        application = MembershipApplication.objects.create(user=self.user, society=self.society)
        self.assertEqual(str(application), f"Application of {self.user.email} to {self.society.name}")

    def test_society_registration_str(self):
        registration = SocietyRegistration.objects.create(name="Pending Society", applicant=self.user, status="pending")
        self.assertEqual(str(registration), f"{registration.name} ({registration.get_status_display()}) - Applicant: {registration.applicant.username}")

    def test_extra_form_str(self):
        registration = SocietyRegistration.objects.create(name="Pending Society", applicant=self.user, status="pending")
        extra_form = ExtraForm.objects.create(society_registration=registration)
        self.assertEqual(str(extra_form), f"Extra Form for {registration.name}")

    def test_widget_str(self):
        widget = Widget.objects.create(society=self.society, widget_type="form")
        self.assertEqual(str(widget), f"{widget.get_widget_type_display()} for {self.society.name}")
