from django.urls import path
from .views import eventspage
from .views import EventListAPIView
from .views import event_list
from .views import event_map
from .views import create_event
from .views import auto_edit_news,
urlpatterns = [
    path('', eventspage, name='eventspage'),
    path("api/", EventListAPIView.as_view(), name="event-list"),
    path("api/events/", event_list, name="event_list"),
    path("event-map/", event_map, name="event_map"),
    path('create/', create_event, name='create_event'),
    path('create/<int:society_id>/', create_event, name='event_create'),
    path('auto_news/<int:event_id>/', auto_edit_news, name='auto_edit_news'),
]


