import django_filters
from django.utils.timezone import now, timedelta
from django.db import models
from apps.societies.models import Society
from apps.events.models import Event
from apps.news.models import News

DATE_FILTER_CHOICES = {
    "today": now().date(),
    "this_week": now().date() - timedelta(days=7),
    "this_month": now().date().replace(day=1),
    "next_3_months": now().date() + timedelta(days=90),
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
    society_type = django_filters.CharFilter(field_name="society__society_type", lookup_expr="icontains")  # Filter by Society Type
    price_range = django_filters.RangeFilter()
    is_free = django_filters.BooleanFilter(method='filter_is_free')
    member_only = django_filters.BooleanFilter()
    date = django_filters.ChoiceFilter(choices=[(key, key) for key in DATE_FILTER_CHOICES], method="filter_by_date")

    def filter_by_date(self, queryset, name, value):
        if value in DATE_FILTER_CHOICES:
            return queryset.filter(date_updated__gte=DATE_FILTER_CHOICES[value])
        return queryset

    def filter_has_space(self, queryset, name, value):
        if value:
            return queryset.filter(members_count__lt=models.F('max_capacity'))
        return queryset

    def filter_is_free(self, queryset, name, value):
        if value:
            return queryset.filter(price_range=0)
        return queryset

    class Meta:
        abstract = True  # This ensures it doesn't create a standalone filter class


class SocietyFilter(GlobalFilterSet):
    class Meta:
        model = Society
        fields = ['has_space', 'society_type', 'price_range', 'is_free']


class EventFilter(GlobalFilterSet):
    class Meta:
        model = Event
        fields = ['has_space', 'date', 'location', 'society', 'society_type', 'member_only', 'price_range', 'is_free']


class NewsFilter(GlobalFilterSet):
    class Meta:
        model = News
        fields = ['society', 'society_type', 'date', 'member_only']
