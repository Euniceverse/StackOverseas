# apps/events/filter.py
import django_filters
from django.db.models import Count, F
from apps.events.models import Event

class EventFilter(django_filters.FilterSet):
    """
    프론트엔드에서 넘기는 쿼리 파라미터들을
    실제 DB 필드와 매핑해주는 커스텀 FilterSet
    """

    # 1) event_type: 예) ?event_type=sports
    event_type = django_filters.CharFilter(field_name='event_type', lookup_expr='exact')

    # 2) member_only: 예) ?member_only=true 혹은 ?member_only=false
    member_only = django_filters.BooleanFilter(field_name='member_only')

    # 3) fee_min, fee_max: 예) ?fee_min=10&fee_max=50
    fee_min = django_filters.NumberFilter(field_name='fee', lookup_expr='gte')
    fee_max = django_filters.NumberFilter(field_name='fee', lookup_expr='lte')

    # 4) location: 예) ?location=london
    location = django_filters.CharFilter(field_name='location', lookup_expr='exact')

    # 5) availability: (가상 필드) ?availability=available / full / waiting
    #    capacity와 registrations(신청자 수)를 비교해 자리 여부를 필터링
    availability = django_filters.CharFilter(method='filter_availability')

    class Meta:
        model = Event
        fields = []  # 여기서는 모든 필터를 개별 필드로 정의했으므로 빈 리스트

    def filter_availability(self, queryset, name, value):
        """
        capacity와 registrations 수를 비교해서
        'available', 'full', 'waiting'을 필터링
        """
        # registrations 수(= reg_count)를 annotate
        queryset = queryset.annotate(reg_count=Count('registrations'))

        if value == 'available':
            return queryset.filter(capacity__isnull=False, reg_count__lt=F('capacity'))
        elif value == 'full':
            return queryset.filter(capacity__isnull=False, reg_count=F('capacity'))
        elif value == 'waiting':
            return queryset.filter(capacity__isnull=False, reg_count__gt=F('capacity'))

        # 그 외 값이면 필터 미적용
        return queryset
