from config.constants import (
    MAX_NAME, MAX_DESCRIPTION, MAX_LOCATION, 
    EVENT_TYPE_CHOICES
)
from apps.societies.models import Society
from django.core.validators import MinValueValidator
from decimal import Decimal
from django import forms

class NewEventForm(forms.Form):
    """Form to submit new event requests."""

    name = forms.CharField(
        max_length=MAX_NAME,
        min_length=1,
        label="Write your event name!",
        required=True,
    )

    description = forms.CharField(
        max_length=MAX_DESCRIPTION,
        widget=forms.Textarea,
        label="Write about your event."
    )

    event_type = forms.ChoiceField(
        choices=EVENT_TYPE_CHOICES,
        required=True,
    )

    date = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}
        )
    )

    keyword = forms.CharField(
        max_length=50,
        required=False, 
    )

    location = forms.CharField(
        max_length=MAX_LOCATION,
        required=True,
        help_text="Enter location such as 'London' or 'Online'."
    )

    capacity = forms.IntegerField(
        required=True,
        validators=[MinValueValidator(1)]
    )

    member_only = forms.BooleanField(
        initial=False, 
        required=False,
    )

    fee = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    is_free = forms.BooleanField(
        initial=True,
        required=False,
    )

    # society = forms.ModelMultipleChoiceField(
    #    queryset=Society.objects.all(),
    #    required=True,
    #    widget=forms.CheckboxSelectMultiple,
    #    help_text="Select one or more societies hosting the event."
    #)

    def clean_fee(self):
        fee = self.cleaned_data.get("fee", Decimal("0.00"))

        if fee > Decimal("0.00"):
            self.cleaned_data["is_free"] = False
        return fee

    def clean(self):
        cleaned_data = super().clean()
        fee = cleaned_data.get("fee", Decimal("0.00"))
        is_free = cleaned_data.get("is_free", True)

        if fee > Decimal("0.00"):
            cleaned_data["is_free"] = False

        return cleaned_data
    

