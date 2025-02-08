from django.db import models
from apps.users.models import CustomUser
from apps.societies.models import Society
from config.constants import MAX_NAME, MAX_DESCRIPTION, MAX_LOCATION
from django.core.validators import MinValueValidator
from decimal import Decimal

class Event(models.Model):
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
    
    location = models.CharField(
        max_length=MAX_LOCATION
    )

    limit = models.IntegerField(
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