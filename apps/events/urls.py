from django.urls import path
from .views import (
    eventspage,
    create_event,
    auto_edit_news,
    EventListAPIView,
    EventDetailAPIView,
    event_detail,
    event_payment,
    event_registration,
)
 
urlpatterns = [
    path('', eventspage, name='eventspage'),
    path("api/", EventListAPIView.as_view(), name="event-list"),
    path('create/<int:society_id>/', create_event, name='event_create'),
    path('auto_news/<int:event_id>/', auto_edit_news, name='auto_edit_news'),
    path("event/<int:event_id>/", event_detail, name="event_detail"),
    path("register/<int:event_id>/", event_registration, name="event_registration"),
    path("payment/<int:event_id>/", event_payment, name="event_payment"),
   
]