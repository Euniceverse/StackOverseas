from django import forms
from config.constants import VISIBILITY_CHOICES, SOCIETY_TYPE_CHOICES
from .models import SocietyRegistration

class NewSocietyForm(forms.ModelForm):
    """Form for creating a new society application."""
    society_type = forms.ChoiceField( 
        choices=SOCIETY_TYPE_CHOICES,
        label="Society Type"
    )
    
    extra_form_needed = forms.BooleanField(
        required=False,
        label="Do you require an extra form for members?",
        help_text="Check this if you want to collect additional information from new members."
    )

    tags = forms.CharField(
        max_length=255,
        required=False,
        label="Tags",
        help_text="Comma-separated tags (e.g., 'music, live events')"
    )

    class Meta:
        model = SocietyRegistration
        fields = ["name", "description", "society_type", "visibility", "extra_form_needed"]

    def clean_name(self):
        """Ensure society name is unique"""
        name = self.cleaned_data.get("name")
        if SocietyRegistration.objects.filter(name=name).exists():
            raise forms.ValidationError("A society with this name already exists. Please choose another.")
        return name

    def clean_tags(self):
        """Clean tags input"""
        tags = self.cleaned_data.get("tags", "")
        if isinstance(tags, list): 
            return tags
        return [tag.strip() for tag in tags.split(",") if tag.strip()]

