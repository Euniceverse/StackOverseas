from django.db import models
from django.conf import settings
from django.apps import apps
from config.constants import VISIBILITY_CHOICES


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
