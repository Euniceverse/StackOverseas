from django.db import models
from django.conf import settings
from django.apps import apps
from apps.users.models import CustomUser
from config.constants import VISIBILITY_CHOICES
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
