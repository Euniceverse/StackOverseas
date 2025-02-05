from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import CustomUser
import re
from django.utils import timezone

class UserForm(forms.ModelForm):
    class Meta:
        """Form options."""
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'preferred_name']

class LogInForm(forms.Form):
    email = forms.CharField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password.")
        return cleaned_data

    def get_user(self):
        """Returns authenticated user if possible."""
        if not self.is_valid():
            return None
        return authenticate(
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('password')
        )

class NewPasswordMixin(forms.Form):
    """Form mixin for new_password and password_confirmation fields."""
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        min_length=8,  # <-- Added minimum length requirement
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase character and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Validate that the password and confirmation match."""
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""

        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(email=self.user.email, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""
    class Meta:
        """Form options."""

        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'preferred_name']

    def clean_email(self):
        """Validate that the email is a .ac.uk address."""
        email = self.cleaned_data.get('email')
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.ac\.uk$", email):
            raise forms.ValidationError("Only .ac.uk email addresses are allowed.")
        return email


    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = CustomUser.objects.create_user(
            email=self.cleaned_data.get('email'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            preferred_name=self.cleaned_data.get('preferred_name'),
            password=self.cleaned_data.get('new_password'),
        )

        return user
