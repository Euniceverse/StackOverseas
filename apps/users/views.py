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

def accountpage(request):
    return render(request, "account.html")

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
        form = LogInForm(request.POST)  # Pass POST data correctly
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                return redirect("home")  # Redirect to the homepage or another page
        messages.error(request, "Invalid email or password.")
        return render(request, self.template_name, {"form": form})

def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')

class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('home')


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


from django.utils.crypto import get_random_string

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
        activation_link = f"http://{settings.DOMAIN_NAME}{reverse('activate', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user_data['email'])), 'token': activation_token})}"

        print(f"Generated activation link: {activation_link}")  # Debugging output

        mail_subject = "Activate your account"
        message = render_to_string("acc_active_email.html", {
            "user": user_data,
            "domain": settings.DOMAIN_NAME,
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
        user.save()

        # Clear cached data
        cache.delete(token)
        login(request, user)
        messages.success(request, "Account activated successfully!")
        return redirect("home")
    except Exception as e:
        return HttpResponse("Activation link is invalid!")
