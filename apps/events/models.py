import datetime
from django.db import models
from config.constants import (
    MAX_NAME, MAX_DESCRIPTION,
    MAX_LOCATION,
    EVENT_TYPE_CHOICES,
    REGISTRATION_STATUS_CHOICES,
    MAX_KEYWORD,
    MAX_DIGIT,)
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings
from apps.societies.models import Society
from django.conf import settings


class Event(models.Model):
    """Model representing an event (e.g. a student society meetup)."""

    society = models.ManyToManyField(
        Society,
    )

    name = models.CharField(
        max_length=MAX_NAME,
    )

    description = models.TextField(
        max_length=MAX_DESCRIPTION,
    )

    date = models.DateTimeField(
        null=False,
    )

    start_time = models.TimeField(
        null=False,
        default=datetime.time(9, 0),
    )

    end_time = models.TimeField(
        null=True,
        blank=True,
    )

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES
    )

    keyword = models.CharField(
      max_length=MAX_KEYWORD,
    )

    location = models.CharField(
        max_length=MAX_LOCATION
    )

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    capacity = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)]
    )

    member_only = models.BooleanField(
        default=False,
    )

    fee = models.DecimalField(
        max_digits=MAX_DIGIT,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    # fee_general = models.DecimalField(
    #     max_digits=MAX_DIGIT,
    #     decimal_places=2,
    #     default=Decimal("0.00"),
    #     validators=[MinValueValidator(Decimal("0.00"))]
    # )

    # fee_member = models.DecimalField(
    #     max_digits=MAX_DIGIT,
    #     decimal_places=2,
    #     default=Decimal("0.00"),
    #     validators=[MinValueValidator(Decimal("0.00"))]
    # )


    is_free = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.event_type}"

    def is_full(self):
        """Check if the event is full based on its capacity."""
        return self.registrations.count() >= self.capacity if self.capacity else False

    def is_user_registered(self, user):
        """Check if the user is already registered for this event."""
        return self.registrations.filter(user=user).exists()

    def register_user(self, user, status='accepted'):
        """Register a user for this event if possible."""
        if self.is_user_registered(user):
            raise ValueError("User is already registered for this event.")
        if self.is_full():
            raise ValueError("Event is full.")

        # Create registration
        registration = EventRegistration.objects.create(event=self, user=user, status=status)
        return registration
class Host(models.Model):
    """Model for Host of Event as many-to-many relationship between Event and Society."""

    event = models.ForeignKey("events.Event", on_delete=models.CASCADE)
    society = models.ForeignKey("societies.Society", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.society.name} hosts {self.event.name}"

class EventRegistration(models.Model):
    """Model representing a user's sign‐up to an event, along with their acceptance/waitlist/rejection status."""

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
