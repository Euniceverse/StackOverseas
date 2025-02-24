from django.shortcuts import render
from apps.news.models import News
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.events.models import Event
from .serializers import EventSerializer
from rest_framework.pagination import PageNumberPagination
from django.utils.timezone import now, make_aware
from datetime import datetime
from .filters import EventFilter  # 경로/파일명은 실제 프로젝트 구조에 맞춰 조정



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

    # ❷ 'filter_backends'는 그대로 두되...
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # ❸ 기존 filterset_fields = ["event_type", "location"] → 'filterset_class' 사용
    filterset_class = EventFilter

    search_fields = ["name", "description"]
    ordering_fields = ["date", "name"]
    ordering = ["date"]

class EventDetailAPIView(generics.RetrieveAPIView):
    """API to get details of a single event"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "id"

class UpcomingEventsAPIView(generics.ListAPIView):
    """API to list only upcoming events"""
    queryset = Event.objects.filter(date__gte=now().date())  # Only future events
    serializer_class = EventSerializer
    pagination_class = StandardResultsSetPagination