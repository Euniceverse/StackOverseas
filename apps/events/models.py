from django.db import models
from apps.users.models import CustomUser
from apps.societies.models import Society
from config.constants import MAX_NAME, MAX_DESCRIPTION, MAX_LOCATION, EVENT_TYPE_CHOICES, REGISTRATION_STATUS_CHOICES
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings

class Event(models.Model):
    """Model representing an event (e.g. a student society meetup)."""

    societies = models.ManyToManyField(
        Society,
        through="Host",
        through_fields=("society", "event"),
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

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES
    )

    keyword = models.CharField(max_length=50, help_text="Tag or keyword for searching (e.g. 'chess').")

    location = models.CharField(
        max_length=MAX_LOCATION
    )

    capacity = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)]
    )

    member_only = models.BooleanField(
        default=True,
    )

    fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )

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
