from django.db import models
from django.conf import settings
from django.apps import apps
from apps.users.models import CustomUser
from config.constants import VISIBILITY_CHOICES, REGISTRATION_STATUS_CHOICES
from django.db.models.signals import m2m_changed
from django.dispatch import receiver


class Society(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    society_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through="Membership",
        related_name="societies_joined",
        blank=True
    )

    location = models.CharField(max_length=255, blank=True, null=True) # Nehir

    members_count = models.IntegerField(default=0)
    price_range = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)

    membership_request_required = models.BooleanField(default=False)

    visibility = models.CharField(
        max_length=7,  # private or public
        choices=VISIBILITY_CHOICES,
        default='Private'
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="managed_societies"
    )


    # Check whether this society is approved and can be customise
    def is_customisable(self):
        return self.status == 'approved'

    def get_events(self):
        """Lazy reference to events to avoid circular dependency."""
        Event = apps.get_model("events", "Event")
        return Event.objects.filter(host__society=self)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


# should be in constants
class MembershipRole(models.TextChoices):
    MANAGER = 'manager', 'Manager'
    CO_MANAGER = 'co_manager', 'Co-Manager'
    EDITOR = 'editor', 'Editor'
    MEMBER = 'member', 'Member'

class MembershipStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'

class Membership(models.Model):
    """
    Intermediate table linking CustomUser and Society 
    so each user in a society can have a role and a status.
    """
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='society_memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_memberships')
    role = models.CharField(max_length=20, choices=MembershipRole.choices, default=MembershipRole.MEMBER)
    status = models.CharField(max_length=20, choices=MembershipStatus.choices, default=MembershipStatus.PENDING)

    def __str__(self):
        return f"{self.user.email} - {self.society.name} ({self.role})"

@receiver(m2m_changed, sender=Society.members.through)
def update_members_count(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        instance.members_count = instance.members.filter(is_active=True).count()
        instance.save()




class RequirementType(models.TextChoices):
    NONE = 'none', 'No Extra Requirements'
    QUIZ = 'quiz', 'Quiz (Yes/No Questions)'
    MANUAL = 'manual', 'Manual Approval (Essay/PDF)'

class SocietyRequirement(models.Model):
    """
    Defines how a society wants to handle membership applications:
    1) none -> auto-approve
    2) quiz -> store up to 5 yes/no questions
    3) manual -> essay/pdf for manager approval
    """
    society = models.OneToOneField(
        Society,
        on_delete=models.CASCADE,
        related_name='requirement'
    )
    requirement_type = models.CharField(
        max_length=10,
        choices=RequirementType.choices,
        default=RequirementType.NONE
    )
    # For quiz
    threshold = models.PositiveIntegerField(
        default=1,
        help_text="Minimum number of correct answers required for auto-approval."
    )
    # For manual
    requires_essay = models.BooleanField(default=False)
    requires_portfolio = models.BooleanField(default=False)

    def __str__(self):
        return f"Requirement for {self.society.name} ({self.get_requirement_type_display()})"


class SocietyQuestion(models.Model):
    """
    If requirement_type=quiz, store up to 5 yes/no questions
    plus the correct boolean answer.
    """
    society_requirement = models.ForeignKey(
        SocietyRequirement,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.CharField(max_length=255)
    correct_answer = models.BooleanField()  # True=Yes is correct, False=No is correct

    def __str__(self):
        return f"Q: {self.question_text} (Correct={self.correct_answer})"


class MembershipApplication(models.Model):
    """
    Stores the user's actual application or submission,
    including quiz answers or essay upload. 
    Managers can view this if manual approval is needed.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='society_membership_applications'
    )
    society = models.ForeignKey(
        Society,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    # For quiz answers, store as a JSON or pickled field for simplicity
    answers_json = models.JSONField(
        default=dict,
        blank=True
    )
    # For manual essay / portfolio
    essay_text = models.TextField(blank=True)
    portfolio_file = models.FileField(
        upload_to='society_portfolios/',
        blank=True, null=True
    )
    # Track the outcome
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return f"Application of {self.user.email} to {self.society.name}"

      
class SocietyRegistration(models.Model):
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="society_applications"
    )
    
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    society_type = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    status = models.CharField(
        max_length=10, 
        choices=REGISTRATION_STATUS_CHOICES, 
        default='waitlisted'
    )

    extra_form_needed = models.BooleanField(default=False)
    
    extra_form = models.OneToOneField(
        'SocietyExtraForm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registration",
        help_text="Reference to the extra form for society registration."
    )
    
    visibility = models.CharField(
        max_length=7,  
        choices=VISIBILITY_CHOICES,
        default='Private'
    )

    def has_extra_form(self):
        """Check if this society has an extra form."""
        return self.extra_form is not None

    def get_extra_form_schema(self):
        """Retrieve the extra form schema if available."""
        return self.extra_form.form_schema if self.has_extra_form() else None

    def __str__(self):
        return f"{self.name} ({self.get_status_display()}) - Applicant: {self.applicant.email}"

    
class SocietyExtraForm(models.Model):
    society_registration = models.OneToOneField(
        'SocietyRegistration',
        on_delete=models.CASCADE,
        related_name="extra_form_entry",
        help_text="Custom form for society membership applications."
    )

    form_schema = models.JSONField(
        help_text="JSON representation of the extra form fields."
    )

    def __str__(self):
        return f"Extra Form for {self.society_registration.name}"

class Widget(models.Model):
    WIDGET_TYPES = [
        ("announcements", "Announcements"),
        ("events", "Events"),
        ("gallery", "Gallery"),
        ("contacts", "Contact Information"),
        ("featured", "Featured Members"),
        ("leaderboard", "Leaderboard"),
        ("news", "News")
    ]
    
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name="widgets")
    widget_type = models.CharField(max_length=50, choices=WIDGET_TYPES)
    position = models.PositiveIntegerField(default=0) 
    custom_html = models.TextField(blank=True, null=True) 
    position = models.PositiveIntegerField(default=0) 

    class Meta:
        ordering = ["position"]
        
    def __str__(self):
        return f"{self.get_widget_type_display()} for {self.society.name}"
