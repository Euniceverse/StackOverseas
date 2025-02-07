from django.urls import path
from .views import societiespage
 
urlpatterns = [
    path('', societiespage, name='societiespage'),
]