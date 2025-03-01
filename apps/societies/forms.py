from django import forms
from config.constants import VISIBILITY_CHOICES, SOCIETY_TYPE_CHOICES
from .models import (
    Society,
    Membership,
)
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

class JoinSocietyForm(forms.Form):
    """
    A single form that can handle any of the 3 requirement types:
     - none: auto-approve
     - quiz: up to 5 yes/no questions
     - manual: essay, optional PDF
    """
    
    essay_text = forms.CharField(
        widget=forms.Textarea, required=False, label="Essay / Statement of Purpose"
    )
    portfolio_file = forms.FileField(required=False, label="Portfolio / PDF")

    def __init__(self, society=None, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.society = society
        self.user = user

        from .models import SocietyRequirement, RequirementType
        
        self.req = None

        if society:
            # Attempt to fetch SocietyRequirement
            self.req = getattr(society, 'requirement', None)

        # If there's no requirement record, treat it as "none"
        req_type = RequirementType.NONE
        if self.req:
            req_type = self.req.requirement_type

        if req_type == RequirementType.QUIZ:
            # Build yes/no fields for each question
            for q in self.req.questions.all():
                field_name = f"question_{q.id}"
                self.fields[field_name] = forms.ChoiceField(
                    choices=[('yes', 'Yes'), ('no', 'No')],
                    label=q.question_text,
                    widget=forms.RadioSelect,
                    required=True
                )

        elif req_type == RequirementType.MANUAL:
            # If requires_essay or requires_portfolio, keep the fields visible 
            # (We already added essay_text + portfolio_file above)
            if not self.req.requires_essay:
                self.fields['essay_text'].widget = forms.HiddenInput()
            if not self.req.requires_portfolio:
                self.fields['portfolio_file'].widget = forms.HiddenInput()
        else:
            # requirement_type = 'none'
            # No fields needed, so hide essay/portfolio in case
            self.fields['essay_text'].widget = forms.HiddenInput()
            self.fields['portfolio_file'].widget = forms.HiddenInput()

    def clean(self):
        """
        For quiz: verify we have answers, we'll do final pass in the view.
        For manual: just ensure we have essay/portfolio if required.
        """
        cleaned_data = super().clean()
        if self.req and self.req.requirement_type == RequirementType.MANUAL:
            if self.req.requires_essay and not cleaned_data.get('essay_text'):
                self.add_error('essay_text', 'An essay is required.')
            if self.req.requires_portfolio and not cleaned_data.get('portfolio_file'):
                self.add_error('portfolio_file', 'A PDF portfolio is required.')
        return cleaned_data

    def create_membership_and_application(self):
        """
        Main function called in the view after is_valid().
        1) If none => auto-approve
        2) If quiz => check correctness, possibly auto-approve or reject
        3) If manual => membership is pending, manager will decide
        """
        application = MembershipApplication.objects.create(
            user=self.user,
            society=self.society
        )

        final_status = None  # 'approved' / 'rejected' / 'pending'
        if not self.req:
            # No record => treat as none => auto-approve
            final_status = 'approved'
        else:
            req_type = self.req.requirement_type
            if req_type == RequirementType.NONE:
                final_status = 'approved'
            elif req_type == RequirementType.QUIZ:
                # Compare user answers vs. correct answers
                correct_count = 0
                total_questions = self.req.questions.count()
                user_answers = {}
                for q in self.req.questions.all():
                    field_name = f"question_{q.id}"
                    user_value = self.cleaned_data.get(field_name, None)
                    is_yes = (user_value == 'yes')
                    user_answers[str(q.id)] = user_value
                    if is_yes == q.correct_answer:
                        correct_count += 1

                # Save answers in the application
                application.answers_json = user_answers
                # Auto-approve if correct_count >= threshold
                if correct_count >= self.req.threshold:
                    final_status = 'approved'
                else:
                    final_status = 'rejected'
            elif req_type == RequirementType.MANUAL:
                # Store essay / portfolio in the application
                essay = self.cleaned_data.get('essay_text', '')
                pdf = self.cleaned_data.get('portfolio_file', None)
                application.essay_text = essay
                if pdf:
                    application.portfolio_file = pdf
                # This means manager must do final approval
                final_status = 'pending'

        # Save the application
        application.is_approved = (final_status == 'approved')
        application.is_rejected = (final_status == 'rejected')
        application.save()

        # If final_status = approved => create or update membership
        # If final_status = rejected => membership won't exist
        # If final_status = pending => create membership but set status='pending' 
        if final_status in ['approved', 'pending']:
            # Check if membership already exists
            membership, created = Membership.objects.get_or_create(
                society=self.society, user=self.user,
                defaults={'role': 'member', 'status': 'pending'}
            )
            # If final_status=approved => set membership.status='approved'
            if final_status == 'approved':
                membership.status = 'approved'
            else:
                membership.status = 'pending'
            membership.save()
        # If final_status='rejected', do nothing (or remove membership if it existed)
        if final_status == 'rejected':
            # Optionally remove membership if they tried and failed
            Membership.objects.filter(society=self.society, user=self.user).delete()

        return application

        

    

