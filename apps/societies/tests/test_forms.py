from django.test import TestCase
from django import forms
from decimal import Decimal
from societies.forms import NewSocietyForm, JoinSocietyForm
from societies.models import SocietyRegistration, Society, Membership, MembershipApplication, SocietyRequirement, RequirementType, Question
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.users.models import CustomUser
from config.constants import SOCIETY_TYPE_CHOICES


class NewSocietyFormTest(TestCase):
    """Testing for NewSocietyForm."""
    
    def setUp(self):
        """Set up a test user for SocietyRegistration"""
        self.user = CustomUser.objects.create_user(
            email="test@university.ac.uk",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            password="Password123"
        )
        
    def test_valid_form(self):
        """Test if the form is valid with correct data."""
        form_data = {
            'name': 'StackOverseas',
            'description': 'This is an arts club.',
            'society_type': 'arts',
            'visibility': 'Private',
        }
        form = NewSocietyForm(data=form_data)        
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_fields(self):
        """Test if the form is invalid when required fields are missing."""
        form_data = {
            'description': 'Missing name field.',
            'society_type': 'arts',
            'visibility': 'Private',
        }
        form = NewSocietyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors) 
    
    def test_clean_fee(self):
        """Test clean_fee method."""
        form_data = {'fee': Decimal("10.00")}
        form = NewSocietyForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data['is_free'])
    
    def test_clean_fee_zero(self):
        """Test clean_fee with zero value."""
        form_data = {'fee': Decimal("0.00")}
        form = NewSocietyForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data['is_free'])


    def test_invalid_form_duplicate_name(self):
        """Test if the form rejects duplicate society names."""
        SocietyRegistration.objects.create(
            name='StackOverseas',
            description='Original club.',
            society_type='arts',
            visibility='Private',
            applicant=self.user, 
        )
        form_data = {
            'name': 'StackOverseas',  
            'description': 'Traying to duplicate.',
            'society_type': 'rts',
            'visibility': 'Private',
        }
        form = NewSocietyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('base_location', form.errors)
        self.assertIn('society_type', form.errors)
        self.assertIn('name', form.errors)

    def test_society_type_choices(self):
        form = NewSocietyForm()
        self.assertEqual(
            list(form.fields['society_type'].choices),
            list(SOCIETY_TYPE_CHOICES)
        )

    def test_dynamic_choices(self):
        from config.constants import SOCIETY_TYPE_CHOICES
        
        form = NewSocietyForm()
        self.assertEqual(form.fields['society_type'].choices, SOCIETY_TYPE_CHOICES)

    # to be deleted if we give up tags
    def test_tags_parsing(self):
        """Test if tags are properly parsed into a list."""
        form_data = {
            'name': 'Arts Club',
            'description': 'A arts society',
            'society_type': 'arts',
            'visibility': 'Public',
            'tags': 'arts, ceramics, painting'
        }
        form = NewSocietyForm(data=form_data)
                 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean_tags(), ['arts', 'ceramics', 'painting'])

    def test_invalid_form_exceeding_max_length(self):
        form_data = {
            'name': 'A' * 300,  # Exceeding max length
            'description': 'Valid Description',
            'society_type': 'technology',
            'visibility': 'Public',
        }
        form = NewSocietyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_invalid_form_invalid_choice(self):
        form_data = {
            'name': 'Test Club',
            'description': 'Valid Description',
            'society_type': 'InvalidChoice',  # Invalid choice
            'visibility': 'Public',
        }
        form = NewSocietyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('society_type', form.errors)

    def test_empty_strings(self):
        form_data = {
            'name': '',
            'description': '',
            'society_type': '',
            'visibility': '',
        }
        form = NewSocietyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('description', form.errors)

    def test_clean_name(self):
        """Ensure clean_name correctly validates uniqueness."""
        SocietyRegistration.objects.create(name="UniqueSociety", description="Test description", society_type="arts", visibility="Public", applicant=self.user)
        form = NewSocietyForm(data={'name': 'UniqueSociety'})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_clean_tags(self):
        """Test if clean_tags processes input correctly."""
        form = NewSocietyForm(data={'tags': 'arts, music, literature'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean_tags(), ['arts', 'music', 'literature'])
    
    def test_clean_tags_list_input(self):
        """Ensure clean_tags handles list input."""
        form = NewSocietyForm(data={'tags': ['sports', 'tech']})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean_tags(), ['sports', 'tech'])

    def test_empty_strings(self):
        form_data = {
            'name': '',
            'description': '',
            'society_type': '',
            'visibility': '',
        }
        form = NewSocietyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('description', form.errors)

    def test_clean_name_duplicate(self):
        # Create form data with a duplicate name
        form_data = {
            "name": "Existing Society",
            "description": "A duplicate society",
            "society_type": "type1",
            "visibility": "public",
            "extra_form_needed": False,
        }
        form = NewSocietyForm(data=form_data)
        
        # Form should be invalid due to duplicate name
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(
            form.errors["name"], ["A society with this name already exists. Please choose another."]
        )
    
    def test_clean_name_unique(self):
        # Create form data with a unique name
        form_data = {
            "name": "Unique Society",
            "description": "A new unique society",
            "society_type": "type1",
            "visibility": "public",
            "extra_form_needed": False,
        }
        form = NewSocietyForm(data=form_data)
        
        # Form should be valid
        self.assertTrue(form.is_valid())

    def test_clean_tags_valid(self):
        # Create form data with valid comma-separated tags
        form_data = {
            "name": "Another Society",
            "description": "A society with tags",
            "society_type": "type1",
            "visibility": "public",
            "extra_form_needed": False,
            "tags": "music, live events, culture"
        }
        form = NewSocietyForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["tags"], ["music", "live events", "culture"])
    
    def test_clean_tags_empty(self):
        # Create form data with empty tags
        form_data = {
            "name": "Tagless Society",
            "description": "A society without tags",
            "society_type": "type1",
            "visibility": "public",
            "extra_form_needed": False,
            "tags": ""
        }
        form = NewSocietyForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["tags"], [])
    
    def test_clean_tags_with_spaces(self):
        # Create form data with extra spaces in tags
        form_data = {
            "name": "Spaced Tags Society",
            "description": "A society with extra spaces in tags",
            "society_type": "type1",
            "visibility": "public",
            "extra_form_needed": False,
            "tags": "  music  ,  live events ,  culture  "
        }
        form = NewSocietyForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["tags"], ["music", "live events", "culture"])
    
    def test_clean_tags_list_input(self):
        # Simulate form data with list input instead of string
        form_data = {
            "name": "List Tags Society",
            "description": "A society with list tags",
            "society_type": "type1",
            "visibility": "public",
            "extra_form_needed": False,
            "tags": ["music", "live events", "culture"]
        }
        form = NewSocietyForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["tags"], ["music", "live events", "culture"])


class SocietyFormTests(TestCase):
    def setUp(self):
        self.society = Society.objects.create(name="Test Society")
        self.user = CustomUser.objects.create(username="testuser")

    def test_form_initialization(self):
        form = NewSocietyForm(society=self.society, user=self.user)
        self.assertEqual(form.society, self.society)
        self.assertEqual(form.user, self.user)


    def test_create_membership_and_application_auto_approve(self):
        form = NewSocietyForm(society=self.society, user=self.user)
        application = form.create_membership_and_application()
        self.assertTrue(application.is_approved)
        self.assertFalse(application.is_rejected)
        self.assertTrue(Membership.objects.filter(society=self.society, user=self.user, status='approved').exists())

    def test_create_membership_and_application_quiz_fail(self):
        requirement = SocietyRequirement.objects.create(society=self.society, requirement_type=RequirementType.QUIZ, threshold=2)
        question1 = Question.objects.create(requirement=requirement, question_text="Is this a test?", correct_answer=True)
        question2 = Question.objects.create(requirement=requirement, question_text="Is Python fun?", correct_answer=True)
        form_data = {
            f'question_{question1.id}': 'no',  # Wrong answer
            f'question_{question2.id}': 'yes',  # Correct answer
        }
        form = NewSocietyForm(society=self.society, user=self.user, data=form_data)
        self.assertTrue(form.is_valid())
        application = form.create_membership_and_application()
        self.assertTrue(application.is_rejected)
        self.assertFalse(application.is_approved)

    def test_create_membership_and_application_manual(self):
        requirement = SocietyRequirement.objects.create(society=self.society, requirement_type=RequirementType.MANUAL, requires_essay=True)
        form_data = {
            'essay_text': 'This is my essay.',
        }
        form = NewSocietyForm(society=self.society, user=self.user, data=form_data)
        self.assertTrue(form.is_valid())
        application = form.create_membership_and_application()
        self.assertEqual(application.essay_text, 'This is my essay.')
        self.assertEqual(application.is_approved, False)
        self.assertEqual(application.is_rejected, False)
        self.assertEqual(application.membership.status, 'pending')


class JoinSocietyFormTest(TestCase):
    """Testing for JoinSocietyForm."""

    # def setUp(self):
    #     self.user = CustomUser.objects.create_user(username="testuser")
    #     self.society = Society.objects.create(name="Test Society")
    #     self.requirement = SocietyRequirement.objects.create(society=self.society, requirement_type=RequirementType.QUIZ)
    #     self.question = Question.objects.create(requirement=self.requirement, question_text="Is this a test?", correct_answer=True)

    def setUp(self):
        # Create a user
        self.user = CustomUser.objects.create(username="testuser")
        
        # Create a society
        self.society = Society.objects.create(name="Test Society")
        
        # Create different types of requirements
        self.no_requirement = None
        self.quiz_requirement = SocietyRequirement.objects.create(
            society=self.society, requirement_type=RequirementType.QUIZ
        )
        self.manual_requirement = SocietyRequirement.objects.create(
            society=self.society, requirement_type=RequirementType.MANUAL,
            requires_essay=True, requires_portfolio=True
        )

    def test_clean_method_quiz_requirement(self):
        """Ensure correct validation for quiz-based requirements."""
        form_data = {
            f'question_{self.question.id}': 'yes',
        }
        form = JoinSocietyForm(society=self.society, user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_method_manual_requirement(self):
        """Ensure correct validation for manual requirements."""
        manual_requirement = SocietyRequirement.objects.create(society=self.society, requirement_type=RequirementType.MANUAL, requires_essay=True)
        form_data = {'essay_text': ''}  # Missing required essay
        form = JoinSocietyForm(society=self.society, user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('essay_text', form.errors)

    def test_create_membership_and_application(self):
        """Ensure memberships are created correctly."""
        form = JoinSocietyForm(society=self.society, user=self.user)
        application = form.create_membership_and_application()
        self.assertEqual(application.society, self.society)
        self.assertEqual(application.user, self.user)

    def test_init_no_requirement(self):
        # Initialize form with no requirement
        form = JoinSocietyForm(society=self.society, user=self.user)
        self.assertEqual(form.req, None)
        self.assertTrue("essay_text" in form.fields and isinstance(form.fields["essay_text"].widget, forms.HiddenInput))
        self.assertTrue("portfolio_file" in form.fields and isinstance(form.fields["portfolio_file"].widget, forms.HiddenInput))
    
    def test_init_quiz_requirement(self):
        # Assign quiz requirement to society
        self.society.requirement = self.quiz_requirement
        
        # Initialize form
        form = JoinSocietyForm(society=self.society, user=self.user)
        self.assertEqual(form.req, self.quiz_requirement)
        
        # Ensure quiz-related fields exist
        for question in self.quiz_requirement.questions.all():
            field_name = f"question_{question.id}"
            self.assertIn(field_name, form.fields)
            self.assertEqual(form.fields[field_name].widget.__class__.__name__, "RadioSelect")
    
    def test_init_manual_requirement(self):
        # Assign manual requirement to society
        self.society.requirement = self.manual_requirement
        
        # Initialize form
        form = JoinSocietyForm(society=self.society, user=self.user)
        self.assertEqual(form.req, self.manual_requirement)
        
        # Ensure essay and portfolio fields are visible
        self.assertNotIsInstance(form.fields["essay_text"].widget, forms.HiddenInput)
        self.assertNotIsInstance(form.fields["portfolio_file"].widget, forms.HiddenInput)

    def test_clean_quiz_requirement_missing_answers(self):
        # Assign quiz requirement
        self.society.requirement = self.quiz_requirement
        
        # Initialize form with missing answers
        form = JoinSocietyForm(society=self.society, user=self.user, data={})
        self.assertFalse(form.is_valid())
        for question in self.quiz_requirement.questions.all():
            field_name = f"question_{question.id}"
            self.assertIn(field_name, form.errors)
    
    def test_clean_manual_requirement_missing_essay(self):
        # Assign manual requirement
        self.society.requirement = self.manual_requirement
        
        # Initialize form with missing essay
        form = JoinSocietyForm(society=self.society, user=self.user, data={})
        self.assertFalse(form.is_valid())
        self.assertIn("essay_text", form.errors)
    
    def test_clean_manual_requirement_missing_portfolio(self):
        # Assign manual requirement
        self.society.requirement = self.manual_requirement
        
        # Initialize form with missing portfolio
        form_data = {"essay_text": "This is my essay."}
        form = JoinSocietyForm(society=self.society, user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("portfolio_file", form.errors)
    
    def test_clean_manual_requirement_valid_submission(self):
        # Assign manual requirement
        self.society.requirement = self.manual_requirement
        
        # Initialize form with valid essay and portfolio
        form_data = {"essay_text": "This is my essay."}
        file_data = {"portfolio_file": SimpleUploadedFile("portfolio.pdf", b"dummy data")}
        form = JoinSocietyForm(society=self.society, user=self.user, data=form_data, files=file_data)
        
        self.assertTrue(form.is_valid())


    def setUp(self):
        # Create a user
        self.user = CustomUser.objects.create(username="testuser")
        
        # Create a society
        self.society = Society.objects.create(name="Test Society")
        
        # Create different types of requirements
        self.no_requirement = None
        self.quiz_requirement = SocietyRequirement.objects.create(
            society=self.society, requirement_type=RequirementType.QUIZ, threshold=2
        )
        self.manual_requirement = SocietyRequirement.objects.create(
            society=self.society, requirement_type=RequirementType.MANUAL,
            requires_essay=True, requires_portfolio=True
        )

    def test_create_membership_auto_approve(self):
        # Initialize form with no requirement (auto-approve case)
        form = JoinSocietyForm(society=self.society, user=self.user, data={})
        self.assertTrue(form.is_valid())
        application = form.create_membership_and_application()
        
        self.assertTrue(application.is_approved)
        self.assertFalse(application.is_rejected)
        
        membership = Membership.objects.get(user=self.user, society=self.society)
        self.assertEqual(membership.status, "approved")

    def test_create_membership_quiz_pass(self):
        # Assign quiz requirement to society
        self.society.requirement = self.quiz_requirement
        
        # Simulate passing quiz answers
        quiz_data = {}
        correct_answers = {q.id: "yes" for q in self.quiz_requirement.questions.all()[:2]}
        for q in self.quiz_requirement.questions.all():
            quiz_data[f"question_{q.id}"] = "yes" if q.id in correct_answers else "no"
        
        form = JoinSocietyForm(society=self.society, user=self.user, data=quiz_data)
        self.assertTrue(form.is_valid())
        application = form.create_membership_and_application()
        
        self.assertTrue(application.is_approved)
        
        membership = Membership.objects.get(user=self.user, society=self.society)
        self.assertEqual(membership.status, "approved")

    def test_create_membership_quiz_fail(self):
        # Assign quiz requirement to society
        self.society.requirement = self.quiz_requirement
        
        # Simulate failing quiz answers
        quiz_data = {}
        for q in self.quiz_requirement.questions.all():
            quiz_data[f"question_{q.id}"] = "no"
        
        form = JoinSocietyForm(society=self.society, user=self.user, data=quiz_data)
        self.assertTrue(form.is_valid())
        application = form.create_membership_and_application()
        
        self.assertTrue(application.is_rejected)
        
        with self.assertRaises(Membership.DoesNotExist):
            Membership.objects.get(user=self.user, society=self.society)

    def test_create_membership_manual_pending(self):
        # Assign manual requirement to society
        self.society.requirement = self.manual_requirement
        
        # Simulate valid manual submission
        form_data = {"essay_text": "This is my essay."}
        file_data = {"portfolio_file": SimpleUploadedFile("portfolio.pdf", b"dummy data")}
        form = JoinSocietyForm(society=self.society, user=self.user, data=form_data, files=file_data)
        
        self.assertTrue(form.is_valid())
        application = form.create_membership_and_application()
        
        self.assertFalse(application.is_approved)
        self.assertFalse(application.is_rejected)
        
        membership = Membership.objects.get(user=self.user, society=self.society)
        self.assertEqual(membership.status, "pending")