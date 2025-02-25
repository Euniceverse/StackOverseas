from django.shortcuts import render
from apps.news.models import News
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.events.models import Event
from .serializers import EventSerializer
from rest_framework.pagination import PageNumberPagination
from django.utils.timezone import now, make_aware
from datetime import datetime
from django.utils import timezone
from config.filters import EventFilter
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Event

def eventspage(request):
    """Events page view"""
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "events.html", {"news_list": news_list})

class StandardResultsSetPagination(PageNumberPagination):
    """Pagination for API"""
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class EventListAPIView(generics.ListAPIView):
    """API to list all future events with timezone-aware filtering"""
    queryset = Event.objects.filter(date__gte=make_aware(datetime.now())).order_by("date")
    serializer_class = EventSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["event_type", "location"]
    search_fields = ["name", "description"]
    ordering_fields = ["date", "name"]
    ordering = ["date"]
    filterset_class = EventFilter  # Apply filtering Nehir
class EventDetailAPIView(generics.RetrieveAPIView):
    """API to get details of a single event"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "id"

class UpcomingEventsAPIView(generics.ListAPIView):
    """API to list only upcoming events"""
    queryset = Event.objects.filter(date__gte=timezone.now())  # Only future events
    serializer_class = EventSerializer
    pagination_class = StandardResultsSetPagination


def create_event(request):
    if request.method == "POST":
        name = request.POST["name"]
        city = request.POST["city"]
        location = request.POST["location"]

        # Get latitude & longitude from hidden fields in the form
        latitude = request.POST.get("latitude", None)
        longitude = request.POST.get("longitude", None)

        # Save event with location data
        Event.objects.create(
            name=name,
            city=city,
            location=location,
            latitude=latitude,
            longitude=longitude
        )

        return redirect("event_map")

    return render(request, "event_form.html")

def event_list(request):
    events = Event.objects.all()
    data = [{
        "name": e.name,
        "address": e.location,
        "latitude": e.latitude,
        "longitude": e.longitude
    } for e in events]
    return JsonResponse(data, safe=False)

from django.shortcuts import render

def event_map(request):
    return render(request, "event_map.html")
