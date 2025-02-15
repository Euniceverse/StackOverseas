from django.urls import path
from .views import eventspage
from .views import EventListAPIView  # ✅ Ensure this import exists
 
urlpatterns = [
    path('', eventspage, name='eventspage'),
    path("api/", EventListAPIView.as_view(), name="event-list"),
]