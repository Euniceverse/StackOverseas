from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from datetime import timedelta
import re
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.cache import cache
from django.conf import settings

def validate_ac_uk_email(email):
    """Ensure the email ends with .ac.uk"""
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.ac\.uk$", email):
        raise ValidationError("Only .ac.uk email addresses are allowed.")

class CustomUserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, preferred_name, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name = first_name,
            last_name = last_name,
            preferred_name=preferred_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, preferred_name, password):
        user = self.create_user(email, first_name, last_name, preferred_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, validators=[validate_ac_uk_email])
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    preferred_name = models.CharField(max_length=50)
    last_verified_date = models.DateTimeField(null=True, blank=True)
    annual_verification_date = models.DateTimeField(null=True, blank=True)

    # By default, users are non-admins
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Only superuser is an admin

    objects = CustomUserManager()

    # fixing conflicts with Django's default auth system
    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'preferred_name']

    def can_change_preferred_name(self):
        """Check if the user can change their preferred name."""
        if self.last_verified_date:
            return timezone.now() >= self.last_verified_date + timedelta(days=365)
        return True  # If never changed before, allow it

    def request_email_verification(self):
        """Simulate sending a verification email (this would be handled by an actual email system)."""
        print(f"Verification email sent to {self.email}.")  # In a real app, replace with an actual email service

    def verify_email(self):
        """Mark the email as verified and update last_verified_date."""
        self.last_verified_date = timezone.now()
        self.save()

    def update_preferred_name(self, new_name):
        if not self.can_change_preferred_name():
            raise ValidationError("You can only change your preferred name once a year.")
        self.request_email_verification()
        print("User must verify their email before the name change is completed.")
        return False

    def confirm_preferred_name_change(self, new_name):
        """Confirm the name change after email verification."""
        self.preferred_name = new_name
        self.verify_email()  # Update last_verified_date
        self.save()
        return True

    def check_annual_verification(self):
        """Check if annual verification is needed and handle accordingly."""
        if not self.annual_verification_date:
            return False

        #one_year_ago = timezone.now() - timedelta(days=365)
        #five_years_ago = timezone.now() - timedelta(days=1825)  # 5 years
        one_year_ago = timezone.now() - timedelta(minutes=2)  # 2 minutes
        five_years_ago = timezone.now() - timedelta(minutes=8)  # 8 minutes

        if self.annual_verification_date <= five_years_ago:
            # Delete account if inactive for 5 years
            self.delete()
            return True

        if self.annual_verification_date <= one_year_ago:
            # Deactivate account if verification is older than 1 year
            self.is_active = False
            self.save()
            return True

        return False

    def send_annual_verification_email(self):
        """Send annual verification email reusing existing activation logic."""
        activation_token = get_random_string(50)
        cache_key = f"annual_verify_{activation_token}"

        # Store user email in cache
        cache.set(cache_key, self.email, 3600)  # 1 hour expiry

        # Generate verification link
        verification_link = (
            f"{settings.PROTOCOL}://{settings.DOMAIN_NAME}"
            f"{reverse('annual_verify')}?uid={urlsafe_base64_encode(force_bytes(self.email))}&token={activation_token}"
        )
        mail_subject = "Annual Account Verification Required"
        message = render_to_string("annual_verification_email.html", {
            "user": self,
            "verification_link": verification_link,
        })
        email = EmailMessage(mail_subject, message, to=[self.email])
        email.send()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
