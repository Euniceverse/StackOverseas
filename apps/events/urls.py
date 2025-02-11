from django.urls import path
from .views import eventspage, EventListAPIView

urlpatterns = [
    path("", eventspage, name="eventspage"),
    path("api/", EventListAPIView.as_view(), name="event-list"),
]
