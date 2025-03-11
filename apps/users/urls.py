from django.urls import path
from .views import (
    accountpage, LogInView, log_out, PasswordView, ProfileUpdateView,
    SignUpView, activate, ForgotPasswordView, ResetPasswordView
)

urlpatterns = [
    path('account/', accountpage, name='accountpage'),
    path('login/', LogInView.as_view(), name='log_in'),
    path('logout/', log_out, name='log_out'),
    path('password/', PasswordView.as_view(), name='password'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('signup/', SignUpView.as_view(), name='sign_up'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<token>/', ResetPasswordView.as_view(), name='reset_password'),
]
