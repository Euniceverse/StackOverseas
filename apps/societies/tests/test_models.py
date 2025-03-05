from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.societies.models import (
    Society, Membership, MembershipApplication, SocietyRequirement, SocietyQuestion,
    RequirementType, SocietyRegistration, SocietyExtraForm, Widget
)
from apps.users.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile


class SocietyModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password")
        self.society = Society.objects.create(
            name="Test Society", description="A test society", 
            society_type="type1", manager=self.user, status="approved"
        )
    
    def test_model_creation(self):
        self.assertEqual(Society.objects.count(), 1)
    
    def test_is_customisable(self):
        self.assertTrue(self.society.is_customisable())
    
    def test_get_events(self):
        self.assertEqual(self.society.get_events().count(), 0)
    
    def test_get_events_fail(self):
        with self.assertRaises(Exception):
            self.society.get_events().filter(non_existent_field=True)
    
    def test_update_members_count(self):
        self.society.members.add(self.user)
        self.society.refresh_from_db()
        self.assertEqual(self.society.members_count, 1)
    
    def test_str_representation(self):
        self.assertEqual(str(self.society), f"{self.society.name} ({self.society.get_status_display()})")


class MembershipModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="memberuser", password="password")
        self.society = Society.objects.create(name="Another Society", description="A different test society", society_type="type2", manager=self.user, status="approved")
        self.membership = Membership.objects.create(society=self.society, user=self.user)
    
    def test_model_creation(self):
        self.assertEqual(Membership.objects.count(), 1)
    
    def test_membership_str(self):
        self.assertEqual(str(self.membership), f"{self.user.email} - {self.society.name} ({self.membership.role})")


class MembershipApplicationModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="applicant", password="password")
        self.society = Society.objects.create(name="Application Society", description="A society for testing applications", society_type="type3", manager=self.user, status="approved")
        self.application = MembershipApplication.objects.create(user=self.user, society=self.society, essay_text="This is my application essay.")
    
    def test_model_creation(self):
        self.assertEqual(MembershipApplication.objects.count(), 1)
    
    def test_application_str(self):
        self.assertEqual(str(self.application), f"Application of {self.user.email} to {self.society.name}")


class SocietyRequirementModelTest(TestCase):
    def setUp(self):
        self.society = Society.objects.create(name="Requirement Society", description="A society with requirements", society_type="type4", manager=get_user_model().objects.create(username="requirement_manager"))
        self.requirement = SocietyRequirement.objects.create(society=self.society, requirement_type=RequirementType.MANUAL, requires_essay=True)
    
    def test_model_creation(self):
        self.assertEqual(SocietyRequirement.objects.count(), 1)
    
    def test_requirement_str(self):
        self.assertEqual(str(self.requirement), f"Requirement for {self.society.name} ({self.requirement.get_requirement_type_display()})")


class SocietyQuestionModelTest(TestCase):
    def setUp(self):
        self.society = Society.objects.create(name="Quiz Society", description="A society with quizzes", society_type="type5", manager=get_user_model().objects.create(username="quiz_manager"))
        self.requirement = SocietyRequirement.objects.create(society=self.society, requirement_type=RequirementType.QUIZ)
        self.question = SocietyQuestion.objects.create(society_requirement=self.requirement, question_text="Is this a test question?", correct_answer=True)
    
    def test_model_creation(self):
        self.assertEqual(SocietyQuestion.objects.count(), 1)
    
    def test_question_str(self):
        self.assertEqual(str(self.question), f"Q: {self.question.question_text} (Correct={self.question.correct_answer})")


class SocietyRegistrationModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="registrant")
        self.registration = SocietyRegistration.objects.create(applicant=self.user, name="Registration Test", description="Testing registration", society_type="test-type")
    
    def test_model_creation(self):
        self.assertEqual(SocietyRegistration.objects.count(), 1)
    
    def test_registration_str(self):
        self.assertEqual(str(self.registration), f"{self.registration.name} ({self.registration.get_status_display()}) - Applicant: {self.user.username}")
    
    def test_has_extra_form_false(self):
        self.assertFalse(self.registration.has_extra_form())
    
    def test_has_extra_form_true(self):
        extra_form = SocietyExtraForm.objects.create(society_registration=self.registration, form_schema={"field": "value"})
        self.assertTrue(self.registration.has_extra_form())
    
    def test_get_extra_form_schema_none(self):
        self.assertIsNone(self.registration.get_extra_form_schema())
    
    def test_get_extra_form_schema_valid(self):
        extra_form = SocietyExtraForm.objects.create(society_registration=self.registration, form_schema={"field": "value"})
        self.assertEqual(self.registration.get_extra_form_schema(), {"field": "value"})


class SocietyExtraFormModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="formuser")
        self.registration = SocietyRegistration.objects.create(applicant=self.user, name="Form Society", description="A society with extra forms", society_type="type6")
        self.extra_form = SocietyExtraForm.objects.create(society_registration=self.registration, form_schema={"field": "value"})
    
    def test_model_creation(self):
        self.assertEqual(SocietyExtraForm.objects.count(), 1)
    
    def test_extra_form_str(self):
        self.assertEqual(str(self.extra_form), f"Extra Form for {self.registration.name}")


class WidgetModelTest(TestCase):
    def setUp(self):
        self.society = Society.objects.create(name="Widget Society", description="A society with widgets", society_type="type7", manager=get_user_model().objects.create(username="widget_manager"))
        self.widget = Widget.objects.create(society=self.society, widget_type="events")
    
    def test_model_creation(self):
        self.assertEqual(Widget.objects.count(), 1)
    
    def test_widget_str(self):
        self.assertEqual(str(self.widget), f"{self.widget.get_widget_type_display()} for {self.society.name}")
