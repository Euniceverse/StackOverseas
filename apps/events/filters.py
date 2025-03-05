import django_filters
from django.db.models import Count, F, Q
from apps.events.models import Event

class EventFilter(django_filters.FilterSet):
    """
    프론트엔드에서 넘기는 쿼리 파라미터들을
    실제 DB 필드와 매핑해주는 커스텀 FilterSet
    """
    
    event_type = django_filters.CharFilter(field_name='event_type', lookup_expr='icontains')  # ✅ 부분 매칭 허용
    member_only = django_filters.BooleanFilter(field_name='member_only')
    fee_min = django_filters.NumberFilter(field_name='fee', lookup_expr='gte')
    fee_max = django_filters.NumberFilter(field_name='fee', lookup_expr='lte')
    location = django_filters.CharFilter(field_name='location', lookup_expr='exact')

    class Meta:
        model = Event
        fields = []


    def filter_availability(self, queryset, name, value):
        """ capacity와 registrations 수를 비교하여 필터링 """
        queryset = queryset.annotate(reg_count=Count("registrations"))

        if value == "available":
            return queryset.filter(Q(capacity__gt=F("reg_count")) | Q(capacity__isnull=True))
        elif value == "full":
            return queryset.filter(capacity__isnull=False, reg_count=F("capacity"))
        elif value == "waiting":
            return queryset.filter(capacity__isnull=False, reg_count__gt=F("capacity"))

        return queryset  # 조건이 없으면 필터 미적용

    def filter_event_type(self, queryset, name, value):
        """
        `event_type` 값이 ('other', 'Other') 같은 튜플 문자열이므로 변환 필요
        ('other', 'Other') → 'other' 로 변환하여 필터 적용
        """
        if isinstance(value, str) and "," in value:
            cleaned_value = value.split(",")[0].strip("()' ")  # 첫 번째 값만 추출
        else:
            cleaned_value = value.strip()
        
        return queryset.filter(event_type__icontains=cleaned_value)
