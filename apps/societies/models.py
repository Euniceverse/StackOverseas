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
    
    # Define Many-to-Many field in the Society model instead of User
    members = models.ManyToManyField(CustomUser, related_name="societies", blank=True)

    members_count = models.IntegerField(default=0)

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
    
@receiver(m2m_changed, sender=Society.members.through)
def update_members_count(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        instance.members_count = instance.members.count()
        instance.save()


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
        return f"{self.name} ({self.get_status_display()}) - Applicant: {self.applicant.username}"
    
    
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