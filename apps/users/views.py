from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from apps.users.forms import SignUpForm, LogInForm, PasswordForm, UserForm
from apps.users.models import CustomUser
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.core.cache import cache
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from apps.societies.models import Society, Membership
from apps.societies.functions import get_societies
from django.utils import timezone

@login_required
def accountpage(request):
    # Get user's societies (both member and manager)
    user_societies = get_societies(request.user)

    # Get societies where user is manager
    managed_societies = Society.objects.filter(manager=request.user)

    # Get all memberships for the user
    memberships = Membership.objects.filter(user=request.user).select_related('society')

    return render(request, "account.html", {
        'user': request.user,
        'societies': user_societies,
        'managed_societies': managed_societies,
        'memberships': memberships,
    })

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(View):
    """Display login screen and handle user login."""

    template_name = "log_in.html"

    def get(self, request):
        """Display the login form."""
        form = LogInForm()  # Pass an empty form
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """Handle login attempt."""
        form = LogInForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                # Check if verification is needed
                needs_verification = user.check_annual_verification()
                if needs_verification:
                    user.send_annual_verification_email()
                    messages.warning(request, "Please check your email to verify your account. Your account has been temporarily deactivated for security purposes.")
                    return render(request, self.template_name, {"form": form})

                login(request, user)
                return redirect("home")
        messages.error(request, "Invalid email or password.")
        return render(request, self.template_name, {"form": form})

def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')

class PasswordView(LoginRequiredMixin, View):
    """Display password change screen and handle password change requests."""

    def get(self, request):
        """Instead of showing password form, send verification email."""
        # Generate reset token
        reset_token = get_random_string(50)
        cache_key = f"pwd_reset_{reset_token}"

        # Store email in cache with token
        cache.set(cache_key, request.user.email, 3600)  # Store for 1 hour

        # Send verification email
        reset_link = f"http://{settings.DOMAIN_NAME}{reverse('reset_password', kwargs={'token': reset_token})}"
        mail_subject = "Verify Password Change"
        message = render_to_string("password_reset_email.html", {
            "user": request.user,
            "reset_link": reset_link,
            "is_change": True  # To differentiate between forgot password and change password in template
        })
        email = EmailMessage(mail_subject, message, to=[request.user.email])
        email.send()

        return render(request, 'password_confirmation.html')

class ForgotPasswordView(View):
    template_name = 'forgot_password.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "If an account exists with this email, you will receive a password reset link.")
            return render(request, self.template_name)

        # Generate reset token
        reset_token = get_random_string(50)
        cache_key = f"pwd_reset_{reset_token}"

        # Store email in cache with token
        cache.set(cache_key, email, 3600)  # Store for 1 hour

        # Send reset email
        reset_link = f"http://{settings.DOMAIN_NAME}{reverse('reset_password', kwargs={'token': reset_token})}"
        mail_subject = "Reset your password"
        message = render_to_string("password_reset_email.html", {
            "user": user,
            "reset_link": reset_link,
            "is_change": False  # This is a forgot password request
        })
        email = EmailMessage(mail_subject, message, to=[user.email])
        email.send()

        messages.success(request, "If an account exists with this email, you will receive a password reset link.")
        return render(request, self.template_name)

class ResetPasswordView(View):
    template_name = 'reset_password.html'

    def get(self, request, token):
        # Check if token is valid
        cache_key = f"pwd_reset_{token}"
        email = cache.get(cache_key)

        if not email:
            messages.error(request, "Password reset link is invalid or has expired.")
            return redirect('log_in')

        return render(request, self.template_name)

    def post(self, request, token):
        cache_key = f"pwd_reset_{token}"
        email = cache.get(cache_key)

        if not email:
            messages.error(request, "Password reset link is invalid or has expired.")
            return redirect('log_in')

        password = request.POST.get('new_password')
        password_confirmation = request.POST.get('password_confirmation')

        if password != password_confirmation:
            messages.error(request, "Passwords do not match.")
            return render(request, self.template_name)

        try:
            user = CustomUser.objects.get(email=email)
            user.set_password(password)
            user.save()

            # Clear the reset token
            cache.delete(cache_key)

            messages.success(request, "Password has been reset successfully. Please log in with your new password.")
            return redirect('log_in')
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid request.")
            return redirect('log_in')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = CustomUser
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse("home")


class SignUpView(LoginProhibitedMixin, FormView):
    # ... existing code ...
    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        email = form.cleaned_data['email']
        cache_key = f"email_timeout_{email}"
        if cache.get(cache_key):
            return HttpResponse("Please wait 5 minutes before requesting another verification email.")

        # Generate unique token
        activation_token = get_random_string(50)
        user_data = {
            'email': email,
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
            'preferred_name': form.cleaned_data['preferred_name'],
            'password': form.cleaned_data['new_password']
        }

        # Store data in cache with activation token
        cache.set(activation_token, user_data, 3600)  # Store for 1 hour

        # Send activation email with token
        self.send_activation_email(activation_token, user_data)
        cache.set(cache_key, True, 300)
        return HttpResponse("Please check your email to confirm your account.")

    def send_activation_email(self, activation_token, user_data):
        # Get the current domain from the request
        current_site = get_current_site(self.request)
        activation_link = f"http://{current_site.domain}{reverse('activate', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user_data['email'])), 'token': activation_token})}"

        print(f"Generated activation link: {activation_link}")  # Debugging output

        mail_subject = "Activate your account"
        message = render_to_string("acc_active_email.html", {
            "user": user_data,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user_data['email'])),
            "token": activation_token,
        })
        email = EmailMessage(mail_subject, message, to=[user_data['email']])
        email.send()


def activate(request, uidb64, token):
    try:
        # Retrieve user data from cache using token
        user_data = cache.get(token)
        if not user_data:
            return HttpResponse("Activation link is invalid or has expired!")

        # Verify email from activation link matches cached data
        email = force_str(urlsafe_base64_decode(uidb64))
        if email != user_data['email']:
            return HttpResponse("Activation link is invalid!")

        if CustomUser.objects.filter(email=email).exists():
            return HttpResponse("This email is already registered!")

        # Create user
        user = CustomUser.objects.create_user(
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            preferred_name=user_data['preferred_name'],
            password=user_data['password']
        )
        user.is_active = True
        user.annual_verification_date = timezone.now()
        user.save()

        # Clear cached data
        cache.delete(token)
        login(request, user)
        messages.success(request, "Account activated successfully!")
        return redirect("home")
    except Exception as e:
        return HttpResponse("Activation link is invalid!")

def annual_verify(request, uidb64, token):
    try:
        cache_key = f"annual_verify_{token}"
        email = cache.get(cache_key)

        if not email:
            return HttpResponse("Verification link is invalid or has expired!")

        decoded_email = force_str(urlsafe_base64_decode(uidb64))
        if email != decoded_email:
            return HttpResponse("Verification link is invalid!")

        user = CustomUser.objects.get(email=email)
        user.is_active = True
        user.annual_verification_date = timezone.now()
        user.last_verified_date = timezone.now()
        user.save()

        # Clear cached data
        cache.delete(cache_key)

        # Log in the user after verification
        login(request, user)

        messages.success(request, "Account verified successfully!")
        return redirect("home")
    except Exception as e:
        return HttpResponse("Verification link is invalid!")
