from django.urls import path
from .views import eventspage
 
urlpatterns = [
    path('', eventspage, name='eventspage'),
]