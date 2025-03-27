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
import requests
from django.http import JsonResponse
import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_SECRET_KEY




def user_can_delete_event(user, event):
    """Return True if user is superuser or has manager/co_manager/editor role for any society of the event."""
    if user.is_superuser:
        return True

    # The event may belong to multiple societies (m2m)
    societies = event.society.all()
    allowed_roles = [MembershipRole.MANAGER, MembershipRole.CO_MANAGER, MembershipRole.EDITOR]

    for soc in societies:
        membership = Membership.objects.filter(
            society=soc,
            user=user,
            status=MembershipStatus.APPROVED
        ).first()
        if membership and membership.role in allowed_roles:
            return True

    return False

@login_required
def delete_event(request, event_id):
    """Delete an event if user is manager/co_manager/editor or superuser."""
    event = get_object_or_404(Event, id=event_id)

    # Check permission
    if not user_can_delete_event(request.user, event):
        messages.error(request, "You do not have permission to delete this event.")
        return redirect('eventspage')

    # If authorized, delete the event
    event.delete()
    messages.success(request, "Event deleted successfully.")
    return redirect('eventspage')

@login_required
def eventspage(request):
    """Events page view"""
    my_events_filter = request.GET.get("my_events", False)
    if my_events_filter:
        events = Event.objects.filter(
            registrations__user=request.user,
            registrations__status='accepted'
        ).distinct()
    else:
        events = Event.objects.all()

    events = EventFilter(request.GET, queryset=events).qs
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]

    return render(request, "events.html", {"news_list": news_list, "events": events})

class EventListAPIView(generics.ListAPIView):
    """API to list all future events with timezone-aware filtering"""
    serializer_class = EventSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ["name", "description", "keyword", "location"]
    ordering_fields = ["date", "name"]
    ordering = ["date"]

    def get_queryset(self):
        print("Filter-api-request:", self.request.GET)  # 🔥 디버깅 로그 추가

        queryset = Event.objects.filter(date__gte=make_aware(datetime.now())).order_by("date")

        # ✅ 숫자로 변환하여 필터 적용
        fee_min = self.request.GET.get("fee_min", None)
        fee_max = self.request.GET.get("fee_max", None)

        print(f"📌 Before Conversion: fee_min={fee_min}, fee_max={fee_max}")  # 🔥 변환 전 로그 추가

        try:
            fee_min = int(fee_min) if fee_min and fee_min.isdigit() else 0  # `None` 또는 `""`이면 기본값 0
            fee_max = int(fee_max) if fee_max and fee_max.isdigit() else 999999  # `None` 또는 `""`이면 큰 값으로 처리
        except ValueError:
            fee_min, fee_max = 0, 999999  # 잘못된 값이면 기본값으로 설정

        print(f"📌 After Conversion: fee_min={fee_min}, fee_max={fee_max}")  # 🔥 변환 후 로그 추가

        queryset = queryset.filter(fee__gte=fee_min, fee__lte=fee_max)

        filtered_queryset = EventFilter(self.request.GET, queryset=queryset).qs

        print(f"🎯 Filtered-api-num: {filtered_queryset.count()}")  # 🔥 필터링된 이벤트 개수 출력

        return filtered_queryset


class EventDetailAPIView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "id"

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
    if not (request.user.is_superuser or (membership and membership.role in allowed_roles)):
        messages.error(request, "You do not have permission to create an event.")
        return redirect('society_page', society_id=society.id)

    if request.method == 'POST':
        form = NewEventForm(request.POST)
        if form.is_valid():
            # Debug logging
            print("Form data:", form.cleaned_data)
            print("Coordinates:", form.cleaned_data.get('latitude'), form.cleaned_data.get('longitude'))

            event = Event.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                date=form.cleaned_data['date'],
                event_type=form.cleaned_data['event_type'],
                keyword=form.cleaned_data['keyword'],
                location=form.cleaned_data['location'],
                capacity=form.cleaned_data['capacity'],
                fee=form.cleaned_data['fee'],
                is_free=form.cleaned_data['is_free'],
                latitude=form.cleaned_data['latitude'],
                longitude=form.cleaned_data['longitude'],
            )
            event.society.add(society)

            news_item = News.objects.create(
                event=event,
                society=society,
                title=event.name,
                content=event.description,
                is_published=False,
            )

            # messages.success(request, "Event created successfully!")
            return redirect('auto_edit_news', event_id=event.id)
        else:
            print("Form errors:", form.errors)
    else:
        form = NewEventForm()

    return render(request, 'create_event.html', {
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
    society = event.society.first()

    NewsFormSet = modelformset_factory(News, form=NewsForm, extra=0)
    if request.method == 'POST':
        formset = NewsFormSet(request.POST, request.FILES, queryset=news_qs)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for news_item in instances:
                news_item.society = society
                news_item.is_published = True
                news_item.save()

            messages.success(request, "News updated and published!")
            return redirect('society_page', society_id=society.id)
        else:
            messages.error(request, "Please fill in all required fields before publishing.")
            print("Formset errors:", formset.errors)

    else:
        formset = NewsFormSet(queryset=news_qs)

    return render(request, 'auto_edit_news.html', {
        'event': event,
        'formset': formset,
    })


@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if user is already registered
    if event.is_user_registered(request.user):
        messages.error(request, "You are already registered for this event.")
        return redirect('eventspage')

    # Register the user
    try:
        status = 'accepted' if not event.is_full() else 'waitlisted'
        registration = event.register_user(request.user, status=status)
        messages.success(request, f"You've successfully registered for {event.name}.")
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('eventspage')

from django.shortcuts import render, get_object_or_404
from apps.events.models import Event
from apps.events.models import EventRegistration

def event_registered_users(request, event_id):
    # Fetch the event
    event = get_object_or_404(Event, id=event_id)

    # Get all registered users for the event
    registered_users = EventRegistration.objects.filter(event=event, status='accepted')

    # Pass the event and registered users to the template
    return render(request, 'event_registered_users.html', {
        'event': event,
        'registered_users': registered_users
    })


def event_list(request):
    print("📍 API Request Query Params:", request.GET)
    events = Event.objects.filter(date__gte=make_aware(datetime.now())).order_by("date")

    my_events_filter = request.GET.get("my_events", False)
    print("📍 My Events Filter Value:", my_events_filter)

    if my_events_filter == 'true':
        events = events.filter(
            registrations__user=request.user,
            registrations__status='accepted'
        ).distinct()

    print("📍 Number of Events After Filtering:", events.count())

    events_data = [{
        "id": event.id,
        "name": event.name,
        "event_type": event.event_type,
        "start_datetime": event.date,
        "end_datetime": event.end_time,
        "address": event.location,
        "fee": event.fee,
        "description": event.description,
        "capacity": event.capacity,
        "hosts": ", ".join([society.name for society in event.society.all()]),
        "latitude": event.latitude,
        "longitude": event.longitude
    } for event in events]

    return JsonResponse(events_data, safe=False)
