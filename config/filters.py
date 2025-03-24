import django_filters
from django.db.models import Q, Count, F, ExpressionWrapper, IntegerField
from django.utils.timezone import now, timedelta
from django.db import models
from apps.societies.models import Society
from apps.events.models import Event, EVENT_TYPE_CHOICES
from apps.news.models import News


DATE_FILTER_CHOICES = {
    "today": now().date(),
    "this_week": now().date() - timedelta(days=7),
    "this_month": now().date().replace(day=1),
    "this_year": now().date().replace(month=1, day=1),
}

class GlobalFilterSet(django_filters.FilterSet):
    """Global filters applied to all models."""
    has_space = django_filters.BooleanFilter(method='filter_has_space')
    location = django_filters.CharFilter(lookup_expr='icontains')
    society = django_filters.ModelChoiceFilter(
        queryset=Society.objects.filter(status="approved"),  # Show only approved societies
        empty_label="All Societies"
    )
    society_type = django_filters.CharFilter(field_name="society__society_type", lookup_expr="icontains")
    price_range = django_filters.RangeFilter()
    is_free = django_filters.BooleanFilter(method='filter_is_free')
    member_only = django_filters.BooleanFilter()
    date = django_filters.ChoiceFilter(choices=[(key, key) for key in DATE_FILTER_CHOICES], method="filter_by_date")

    def filter_by_date(self, queryset, name, value):
        if value in DATE_FILTER_CHOICES:
            return queryset.filter(date__gte=DATE_FILTER_CHOICES[value])
        return queryset

    def filter_has_space(self, queryset, name, value):
        if value:
            return queryset.filter(members_count__lt=models.F('max_capacity'))
        return queryset

    def filter_is_free(self, queryset, name, value):
        if value:
            return queryset.filter(fee=0)
        return queryset

    class Meta:
        abstract = True  # This ensures it doesn't create a standalone filter class


class EventFilter(GlobalFilterSet):
    """Event-specific filtering with additional fields for event type and pricing."""
    event_type = django_filters.CharFilter(field_name="event_type", lookup_expr="contains")
    price_range = django_filters.RangeFilter(method='filter_by_price')
    available_slots = django_filters.BooleanFilter(method='filter_available_slots')

    def filter_by_price(self, queryset, name, value):
        if value.start and value.stop:
            return queryset.filter(
                Q(fee__gte=value.start, fee__lte=value.stop) |
                Q(fee_member__gte=value.start, fee_member__lte=value.stop) |
                Q(fee_general__gte=value.start, fee_general__lte=value.stop)
            )
        elif value.start:
            queryset = queryset.filter(
                Q(fee__gte=value.start) |
                Q(fee_member__gte=value.start) |
                Q(fee_general__gte=value.start)
            )
        elif value.stop:
            queryset = queryset.filter(
                Q(fee__lte=value.stop) |
                Q(fee_member__lte=value.stop) |
                Q(fee_general__lte=value.stop)
            )
        return queryset

    def filter_available_slots(self, queryset, name, value):
        queryset = queryset.annotate(
            available_slots=ExpressionWrapper(
                F('capacity') - Count('registrations'),
                output_field=IntegerField()  # 결과를 정수(Integer)로 변환
            )
        )

        if value:
            return queryset.filter(available_slots__gt=0)
        return queryset.filter(available_slots__lte=0)

    class Meta:
        model = Event
        fields = ['event_type', 'location', 'capacity', 'member_only', 'fee', 'fee_general', 'fee_member']


class SocietyFilter(GlobalFilterSet):
    society_type = django_filters.CharFilter(field_name="society_type", lookup_expr="icontains")
    class Meta:
        model = Society
        fields = ['has_space', 'society_type', 'price_range', 'is_free']


class NewsFilter(django_filters.FilterSet):
    society_type = django_filters.CharFilter(method='filter_by_society_type')  # Fix society_type filtering
    society = django_filters.ModelChoiceFilter(
        queryset=Society.objects.filter(status="approved"),
        empty_label="All Societies"
    )
    date = django_filters.ChoiceFilter(choices=[(key, key) for key in DATE_FILTER_CHOICES], method="filter_by_date")

    def filter_by_society_type(self, queryset, name, value):
        """
        Filter news by the society type (extract from related Society model).
        """
        return queryset.filter(society__society_type__icontains=value)

    def filter_by_date(self, queryset, name, value):
        if value in DATE_FILTER_CHOICES:
            return queryset.filter(date_posted__gte=DATE_FILTER_CHOICES[value])
        return queryset

    class Meta:
        model = News
        fields = ['society', 'society_type', 'date']
