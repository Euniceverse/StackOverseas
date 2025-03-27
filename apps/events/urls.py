from django.urls import path
from .views import (
    eventspage,
    create_event,
    auto_edit_news,
    EventListAPIView,
    delete_event,
    event_registered_users,
)

urlpatterns = [
    path('', eventspage, name='eventspage'),
    path("api/", EventListAPIView.as_view(), name="event-list"),
    path('create/<int:society_id>/', create_event, name='event_create'),
    path('auto_news/<int:event_id>/', auto_edit_news, name='auto_edit_news'),
    path('delete/<int:event_id>/', delete_event, name='delete_event'),
    path('event/<int:event_id>/registered_users/', event_registered_users, name='event_registered_users'),
]
