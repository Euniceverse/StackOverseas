from django.db import models
from django.conf import settings
from apps.societies.models import Society

class Event(models.Model):
    """Model representing an event (e.g. a student society meetup)."""

    # Choices for event type
    EVENT_TYPE_CHOICES = [
        ('sports', 'Sports'),
        ('academic', 'Academic'),
        ('arts', 'Arts'),
        ('cultural', 'Cultural'),
        ('social', 'Social'),
        ('other', 'Other'),
    ]

    society = models.ForeignKey(
        Society,
        on_delete=models.CASCADE,
        related_name='events'
    )

    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(
        max_length=255,
        help_text="Specify a city (e.g. 'Manchester') or 'Online'."
    )
    date = models.DateTimeField()
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    keyword = models.CharField(max_length=50, help_text="Tag or keyword for searching (e.g. 'chess').")

    # True if free, False if paid
    is_free = models.BooleanField(default=True)

    # True if only society members can attend, False if open to everyone
    members_only = models.BooleanField(default=False)

    # Maximum number of attendees
    capacity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.event_type}"

class EventRegistration(models.Model):
    """Model representing a user's sign‐up to an event, along with their acceptance/waitlist/rejection status."""

    REGISTRATION_STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('waitlisted', 'Waitlisted'),
        ('rejected', 'Rejected'),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_registrations'
    )
    status = models.CharField(
        max_length=20,
        choices=REGISTRATION_STATUS_CHOICES,
        default='waitlisted'
    )
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.event} - {self.status}"
