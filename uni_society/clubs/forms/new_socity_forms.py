from django import forms
from clubs.choices import VISIBILITY_CHOICES, SOCIETY_TYPE_CHOICES

class NewSocietyForm(forms.Form):
    """Form to submit new society requests."""

    name = forms.CharField(
        max_length=50,
        min_length=1,
        label="Write your society name!"
    )

    description = forms.CharField(
        max_length=100,
        widget=forms.Textarea
        label="Write about your society."
    )

    society_type = forms.ChoiceField(
        choices=choices.SOCIETY_TYPE_CHOICES
    )
    
    visibility = forms.ChoiceField(
        choices=choices.VISIBILITY_CHOICES
    )