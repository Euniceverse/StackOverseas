from django.shortcuts import render, redirect, get_object_or_404
from apps.news.models import News
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.events.models import Event
from .serializers import EventSerializer
from rest_framework.pagination import PageNumberPagination
from django.utils.timezone import now, make_aware
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.events.forms import NewEventForm
from apps.societies.models import Society, Membership, MembershipRole, MembershipStatus
from django.urls import reverse
from apps.news.forms import NewsForm
from apps.news.models import News
from django.forms import modelformset_factory
from django.utils import timezone
from config.filters import EventFilter

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


@login_required
def create_event(request, society_id):
    """
    1) Check user can create an event (manager/co_manager/editor of this society).
    2) Show NewEventForm, let them create an event.
    3) When event is saved, the signal auto-creates news (is_published=False).
    4) Then redirect the user to edit_auto_news so they can finalize that news.
    """
    society = get_object_or_404(Society, id=society_id)

    # Check user membership role:
    membership = Membership.objects.filter(
        society=society,
        user=request.user,
        status=MembershipStatus.APPROVED
    ).first()
    allowed_roles = [MembershipRole.MANAGER, MembershipRole.CO_MANAGER, MembershipRole.EDITOR]
    if not membership or membership.role not in allowed_roles:
        messages.error(request, "You do not have permission to create an event for this society.")
        return redirect('society_detail', society_id=society.id)

    if request.method == 'POST':
        form = NewEventForm(request.POST)
        if form.is_valid():
            event = Event.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                date=form.cleaned_data['date'],
                event_type=form.cleaned_data['event_type'],
                keyword=form.cleaned_data['keyword'],
                location=form.cleaned_data['location'],
                capacity=form.cleaned_data['capacity'],
                member_only=form.cleaned_data['member_only'],
                fee=form.cleaned_data['fee'],
                is_free=form.cleaned_data['is_free'],
            )
            # For the many-to-many societies, you do:
            event.society.set(form.cleaned_data['society']) 

            messages.success(request, "Event created successfully!")
            # The signal will create the News. We redirect to an edit page to let them finalize
            return redirect('auto_edit_news', event_id=event.id)
    else:
        form = NewEventForm()

    return render(request, 'events/create_event.html', {
        'form': form,
        'society': society,
    })

@login_required
def auto_edit_news(request, event_id):
    """
    Fetch all News objects that were auto-created for this Event 
    (should be 1 per hosting society if you used your signal).
    Display them in a formset so the user can finalize or skip.
    """
    event = get_object_or_404(Event, id=event_id)
    news_qs = News.objects.filter(event=event)

    # If there are multiple news items (e.g. multi societies?), we can use a formset:
    NewsFormSet = modelformset_factory(News, form=NewsForm, extra=0)
    if request.method == 'POST':
        formset = NewsFormSet(request.POST, request.FILES, queryset=news_qs)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for news_item in instances:
               
                news_item.is_published = True
                news_item.save()

            messages.success(request, "News updated and published!")
            return redirect('eventspage')
    else:
        formset = NewsFormSet(queryset=news_qs)

    return render(request, 'events/auto_edit_news.html', {
        'event': event,
        'formset': formset,
    })
