from django.urls import path
from .views import accountpage

urlpatterns = [
    path('', accountpage, name='accountpage'),
]
