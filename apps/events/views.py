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

def get_events(societies):
    """
    Retrieve events for the given societies.

    :param societies: Queryset or list of society objects to filter events.
    :return: QuerySet of events belonging to the given societies.
    """
    print(Event.objects.filter(
        date__gte=make_aware(datetime.now()),  # Only future events
        society__in=societies  # Matches any society in the given list
    ).distinct().order_by("date"))
    return Event.objects.filter(
        date__gte=make_aware(datetime.now()),  # Only future events
        society__in=societies  # Matches any society in the given list
    ).distinct().order_by("date")

def eventspage(request):
    """Events page view"""
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "events.html", {"news_list": news_list})

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

        # queryset = Event.objects.filter(date__gte=make_aware(datetime.now())).order_by("date")
        societies = Society.objects.filter(status = "approved", visibility = "Public")
        # print(f"✅ Approved Societies List: {list(societies)}")
        queryset = get_events(societies)

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
            event.society.add(society)

            messages.success(request, "Event created successfully!")
            # The signal will create the News. We redirect to an edit page to let them finalize
            return redirect('auto_edit_news', event_id=event.id)
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

    return render(request, 'auto_edit_news.html', {
        'event': event,
        'formset': formset,
    })

