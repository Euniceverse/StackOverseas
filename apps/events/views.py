from django.shortcuts import render
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.events.models import Event
from .serializers import EventSerializer
from django.utils.timezone import now
from rest_framework.pagination import PageNumberPagination

def eventspage(request):
    """Events page view"""
    return render(request, "events.html")

class StandardResultsSetPagination(PageNumberPagination):
    """Pagination for API"""
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class EventListAPIView(generics.ListAPIView):
    """API to list all future events with filters and pagination"""
    queryset = Event.objects.filter(date__gte=now().date())  # Only future events
    serializer_class = EventSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["event_type", "location"]  # Filter by type or location
    search_fields = ["name", "description"]  # Search in event name and description
    ordering_fields = ["date", "name"]  # Allow ordering by date or name
    

class EventDetailAPIView(generics.RetrieveAPIView):
    """API to get details of a single event"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "id"

class UpcomingEventsAPIView(generics.ListAPIView):
    """API to list only upcoming events"""
    serializer_class = EventSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Event.objects.filter(date__gte=now().date())  # Future events only
