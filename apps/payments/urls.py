from django.urls import path
from .views import create_checkout_session, payment_success, payment_cancel

app_name = "payments"

urlpatterns = [
    path('checkout/', create_checkout_session, name='create_checkout_session'),
    path('success/', payment_success, name='payment_success'),
    path('cancel/', payment_cancel, name='payment_cancel'),
]