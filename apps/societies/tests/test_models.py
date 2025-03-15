from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.societies.models import (
    Society, Membership, MembershipApplication, SocietyRequirement, SocietyQuestion,
    RequirementType, SocietyRegistration, SocietyExtraForm, Widget
)
from apps.users.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile


class SocietyModelTest(TestCase):
    """Test for Society Model."""
    def setUp(self):
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", 
            first_name="Test", 
            last_name="User", 
            preferred_name="Tester",
            password="password"
        )

        self.society = Society.objects.create(
            name="Test Society", 
            description="A test society", 
            society_type="type1", 
            manager=self.user, 
            status="approved"
        )
    
    def test_model_creation(self):
        """Test that a society instance is created successfully."""
        self.assertEqual(Society.objects.count(), 1)
    
    def test_is_customisable(self):
        """Test that a society with status 'approved' is customizable."""
        self.assertTrue(self.society.is_customisable())
    
    def test_get_events(self):
        """Test that get_events method returns an empty queryset when there are no events."""
        self.assertEqual(self.society.get_events().count(), 0)
    
    def test_get_events_fail(self):
        """Test that filtering events with a non-existent field raises an exception."""
        with self.assertRaises(Exception):
            self.society.get_events().filter(non_existent_field=True)
    
    def test_update_members_count(self):
        """Test that adding a member updates the members_count field."""
        self.society.members.add(self.user)
        self.society.refresh_from_db()
        self.assertEqual(self.society.members_count, 1)
    
    def test_str_representation(self):
        """Test the string representation of a Society"""
        self.assertEqual(str(self.society), f"{self.society.name} ({self.society.get_status_display()})")


class MembershipModelTest(TestCase):
    """Test for the Membership Model."""
    def setUp(self):
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            email="memberuser@example.com",
            first_name="Member",
            last_name="User",
            preferred_name="MemberUser",
            password="password"
        )
        
        self.society = Society.objects.create(
            name="Another Society", 
            description="A different test society", 
            society_type="type2", 
            manager=self.user, 
            status="approved"
        )
        
        self.membership = Membership.objects.create(
            society=self.society, 
            user=self.user
        )
    
    def test_model_creation(self):
        """Test that a membership instance is created successfully."""
        self.assertEqual(Membership.objects.count(), 1)
    
    def test_membership_str(self):
        """Test the string representation of a Membership."""
        self.assertEqual(str(self.membership), f"{self.user.email} - {self.society.name} ({self.membership.role})")


class MembershipApplicationModelTest(TestCase):
    """Tests for Membership Application Model."""
    def setUp(self):
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            email="applicant@example.com",
            first_name="Applicant",
            last_name="Test",
            preferred_name="ApplicantTest",
            password="password"
        )
        
        self.society = Society.objects.create(
            name="Application Society",
            description="A society for testing applications",
            society_type="type3",
            manager=self.user,
            status="approved"
        )
        
        self.application = MembershipApplication.objects.create(
            user=self.user,
            society=self.society,
            essay_text="This is my application essay."
        )
    
    def test_model_creation(self):
        """Test that a membership application instance is created successfully."""
        self.assertEqual(MembershipApplication.objects.count(), 1)
    
    def test_application_str(self):
        """Test the string representation of a membership application."""
        self.assertEqual(str(self.application), f"Application of {self.user.email} to {self.society.name}")


class SocietyRequirementModelTest(TestCase):
    """Test for SocietyRequirement Model."""
    def setUp(self):
        """Set up test data."""
        self.manager = get_user_model().objects.create_user(
            email="requirement_manager@example.com",
            first_name="Requirement",
            last_name="Manager",
            preferred_name="ReqManager",
            password="password"
        )

        self.society = Society.objects.create(
            name="Requirement Society", 
            description="A society with requirements", 
            society_type="type4", 
            manager=self.manager
        )
        
        self.requirement = SocietyRequirement.objects.create(
            society=self.society, 
            requirement_type=RequirementType.MANUAL, 
            requires_essay=True
        )
    
    def test_model_creation(self):
        """Test that a society requirement instance is created successfully."""
        self.assertEqual(SocietyRequirement.objects.count(), 1)
    
    def test_requirement_str(self):
        """Test the string representation of a society requirement."""
        self.assertEqual(str(self.requirement), f"Requirement for {self.society.name} ({self.requirement.get_requirement_type_display()})")


class SocietyQuestionModelTest(TestCase):
    """Tests for SocietyQuestion Model."""
    def setUp(self):
        """Set up test data."""
        self.manager = get_user_model().objects.create_user(
            email="quiz_manager@example.com",
            first_name="Quiz",
            last_name="Manager",
            preferred_name="QuizManager",
            password="password"
        )
        
        self.society = Society.objects.create(
            name="Quiz Society", 
            description="A society with quizzes", 
            society_type="type5", 
            manager=self.manager
        )
        
        self.requirement = SocietyRequirement.objects.create(
            society=self.society, 
            requirement_type=RequirementType.QUIZ
        )
        
        self.question = SocietyQuestion.objects.create(
            society_requirement=self.requirement, 
            question_text="Is this a test question?", 
            correct_answer=True
        )
    
    def test_model_creation(self):
        """Tests that a society requirement instance is created successfully."""
        self.assertEqual(SocietyQuestion.objects.count(), 1)
    
    def test_question_str(self):
        """Test the string representation of a society requirement."""
        self.assertEqual(str(self.question), f"Q: {self.question.question_text} (Correct={self.question.correct_answer})")


class SocietyRegistrationModelTest(TestCase):
    """Tests for SocietyRegistration Model."""
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            email="registrant@example.com",
            first_name="Registrant",
            last_name="User",
            preferred_name="Registrant",
            password="password"
        )
        
        self.registration = SocietyRegistration.objects.create(
            applicant=self.user, 
            name="Registration Test", 
            description="Testing registration", 
            society_type="test-type"
        )
    
    def test_model_creation(self):
        """Test that a society registration instance is created successfully."""
        self.assertEqual(SocietyRegistration.objects.count(), 1)
    
    def test_registration_str(self):
        """Test the string representation of a SocietyRegistration."""
        self.assertEqual(str(self.registration), f"{self.registration.name} ({self.registration.get_status_display()}) - Applicant: {self.user.email}")
    
    def test_has_extra_form_false(self):
        """Test that has_extra_form() returns False when no extra form is assigned."""
        self.assertFalse(self.registration.has_extra_form())
    
    def test_has_extra_form_true(self):
        """Test that has_extra_form() returns True after assigning an extra form."""
        extra_form = SocietyExtraForm.objects.create(
            society_registration=self.registration, 
            form_schema={"field": "value"}
        )
        
        self.registration.extra_form = extra_form
        self.registration.save()
        self.registration.refresh_from_db()
        self.assertTrue(self.registration.has_extra_form())
    
    def test_get_extra_form_schema_none(self):
        """Test that get_extra_form_schema() returns None when no extra form is assigned."""
        self.assertIsNone(self.registration.get_extra_form_schema())
    
    def test_get_extra_form_schema_valid(self):
        """Test that get_extra_form_schema() returns the correct form schema when an extra form is assigned."""
        extra_form = SocietyExtraForm.objects.create(
            society_registration=self.registration, 
            form_schema={"field": "value"}
        )
        
        self.registration.extra_form = extra_form
        self.registration.save()
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.get_extra_form_schema(), {"field": "value"})


class SocietyExtraFormModelTest(TestCase):
    """Tests for the SocietyExtraForm model."""
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            email="formuser@example.com",
            first_name="Form",
            last_name="User",
            preferred_name="FormUser",
            password="password"
        )
        self.registration = SocietyRegistration.objects.create(applicant=self.user, name="Form Society", description="A society with extra forms", society_type="type6")
        self.extra_form = SocietyExtraForm.objects.create(society_registration=self.registration, form_schema={"field": "value"})
    
    def test_model_creation(self):
        """Test that a society extra form instance is created successfully."""
        self.assertEqual(SocietyExtraForm.objects.count(), 1)
    
    def test_extra_form_str(self):
        """Test the string representation of a society extra form."""
        self.assertEqual(str(self.extra_form), f"Extra Form for {self.registration.name}")


class WidgetModelTest(TestCase):
    """Tests for the Widget model."""
    def setUp(self):
        """Set up test data."""
        manager = get_user_model().objects.create_user(
            email="widget_manager@example.com",
            first_name="Widget",
            last_name="Manager",
            preferred_name="WidgetManager",
            password="password"
        )

        self.society = Society.objects.create(
            name="Widget Society",
            description="A society with widgets",
            society_type="type7",
            manager=manager
        )

        self.widget = Widget.objects.create(
            society=self.society, 
            widget_type="events"
        )
    
    def test_model_creation(self):
        """Test that a widget instance is created successfully."""
        self.assertEqual(Widget.objects.count(), 1)
    
    def test_widget_str(self):
        """Test the string representation of a widget."""
        self.assertEqual(str(self.widget), f"{self.widget.get_widget_type_display()} for {self.society.name}")