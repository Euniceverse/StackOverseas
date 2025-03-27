from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
from PIL import Image
from io import BytesIO
from apps.panels.forms import (
    CommentForm,
    GalleryForm,
    ImageUploadForm,
    PollForm,
    QuestionForm,
    OptionFormSet
)

class PanelsFormsTests(TestCase):
    """Tests for Panels Forms"""
    
    def test_comment_form_valid(self):
        """Test that a valid comment form passes validation."""
        data = {"content": "This is a test comment."}
        form = CommentForm(data=data)
        self.assertTrue(form.is_valid())

    def test_comment_form_invalid(self):
        """Test that an empty comment form fails validation."""
        data = {"content": ""}
        form = CommentForm(data=data)
        self.assertFalse(form.is_valid())

    def test_gallery_form_valid(self):
        """Test that a valid gallery form passes validation."""
        data = {"title": "Test Gallery", "description": "A description for testing."}
        form = GalleryForm(data=data)
        self.assertTrue(form.is_valid())

    def test_gallery_form_invalid(self):
        """Test that a gallery form without a title fails validation."""
        data = {"title": "", "description": "A description for testing."}
        form = GalleryForm(data=data)
        self.assertFalse(form.is_valid())

    def generate_minimal_png(self):
        # Create a 1x1 pixel image using Pillow.
        image = Image.new("RGB", (1, 1), (255, 0, 0))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_image_upload_form_valid(self):
        """Test that a valid image upload form passes validation."""
        minimal_png = self.generate_minimal_png()
        test_file = SimpleUploadedFile("test.png", minimal_png, content_type="image/png")
        form = ImageUploadForm(files={"image": test_file})
        self.assertTrue(form.is_valid())
        
    def test_poll_form_valid(self):
        """Test that a valid poll form passes validation."""
        deadline = (timezone.now() + timedelta(days=7)).date()
        data = {"title": "Test Poll", "description": "Poll description", "deadline": deadline}
        form = PollForm(data=data)
        self.assertTrue(form.is_valid())

    def test_poll_form_invalid(self):
        """Test that a poll form missing a title fails validation."""
        deadline = (timezone.now() + timedelta(days=7)).date()
        data = {"title": "", "description": "Poll description", "deadline": deadline}
        form = PollForm(data=data)
        self.assertFalse(form.is_valid())

    def test_question_form_valid(self):
        """Test that a valid question form passes validation."""
        data = {"question_text": "What is your favorite color?"}
        form = QuestionForm(data=data)
        self.assertTrue(form.is_valid())

    def test_question_form_invalid(self):
        """Test that a question form with empty text fails validation."""
        data = {"question_text": ""}
        form = QuestionForm(data=data)
        self.assertFalse(form.is_valid())

    def test_option_formset_valid(self):
        """Test that a valid option formset passes validation."""
        data = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-option_text": "Blue",
            "form-1-option_text": "Red",
        }
        formset = OptionFormSet(data=data)
        self.assertTrue(formset.is_valid())
        self.assertEqual(len(formset.forms), 2)

    def test_option_formset_invalid(self):
        """Test that an option formset with missing option_text fails validation."""
        data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-option_text": "",  # empty value should trigger validation error
        }
        formset = OptionFormSet(data=data)
        self.assertFalse(formset.is_valid())
        self.assertIn("option_text", formset.forms[0].errors)
            