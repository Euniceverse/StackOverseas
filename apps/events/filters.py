import django_filters
from django.db.models import Count, F
from apps.events.models import Event


class EventFilter(django_filters.FilterSet):
    """
    django_filters.FilterSet을 활용해
    Query Param -> DB 필터 를 매핑
    """
    # ① event_type: 기본 exact 매칭 (예: `?event_type=sports`)
    event_type = django_filters.CharFilter(field_name='event_type', lookup_expr='exact')

    # ② member_only: Boolean 필터 (예: `?member_only=true` / `?member_only=false`)
    member_only = django_filters.BooleanFilter(field_name='member_only')

    # ③ fee_min / fee_max: DecimalField에 대한 gte, lte 필터
    #    프론트에서 `?fee_min=10&fee_max=50` 이렇게 보내면,
    #    fee >= 10 AND fee <= 50 로 필터
    fee_min = django_filters.NumberFilter(field_name='fee', lookup_expr='gte')
    fee_max = django_filters.NumberFilter(field_name='fee', lookup_expr='lte')

    # ④ location: exact 매칭
    #    (예: `?location=london`)
    location = django_filters.CharFilter(field_name='location', lookup_expr='exact')

    # ⑤ availability: custom method filter
    #    (예: `?availability=available`, `?availability=full`, `?availability=waiting`)
    availability = django_filters.CharFilter(method='filter_availability')

    class Meta:
        model = Event
        # 아래 fields는 "기본적으로" 처리할 수 있는 필드를 지정
        fields = []  # 개별 필드는 위에서 따로 선언했으니 여기는 비워둬도 OK

    def filter_availability(self, queryset, name, value):
        """
        value: 'available' | 'full' | 'waiting' 등
        capacity와 registrations.count() 비교
        """
        # registrations 수를 annotate 해서 비교
        queryset = queryset.annotate(reg_count=Count('registrations'))

        if value == 'available':
            # capacity != null, reg_count < capacity 인 경우
            return queryset.filter(
                capacity__isnull=False,
                reg_count__lt=F('capacity')
            )
        elif value == 'full':
            # capacity != null, reg_count == capacity
            return queryset.filter(
                capacity__isnull=False,
                reg_count=F('capacity')
            )
        elif value == 'waiting':
            # capacity != null, reg_count > capacity
            return queryset.filter(
                capacity__isnull=False,
                reg_count__gt=F('capacity')
            )
        return queryset  # value가 none이거나 예외면 필터 적용 안 함
