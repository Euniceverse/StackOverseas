from django import forms
from config.constants import VISIBILITY_CHOICES, SOCIETY_TYPE_CHOICES

class NewSocietyForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        min_length=1,
        label="Society Name"
    )

    description = forms.CharField(
        max_length=500,
        widget=forms.Textarea,
        label="Describe your society."
    )

    society_type = forms.ChoiceField(
        choices=SOCIETY_TYPE_CHOICES
    )

    base_location = forms.CharField(
        max_length=100,
        required=True,
        label="Base Location",
        help_text="City or region where the society primarily operates."
    )

    tags = forms.CharField(
        max_length=255,
        required=False,
        help_text="Comma-separated tags (e.g. 'music, live events')"
    )