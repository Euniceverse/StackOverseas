from django.urls import path
from .views import accountpage, LogInView, log_out, PasswordView, ProfileUpdateView, SignUpView

urlpatterns = [
    path('account/', accountpage, name='accountpage'),
    path('login/', LogInView.as_view(), name='log_in'),
    path('logout/', log_out, name='log_out'),
    path('password/', PasswordView.as_view(), name='password'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('signup/', SignUpView.as_view(), name='sign_up'),
]
