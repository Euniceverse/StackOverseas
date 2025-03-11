from rest_framework import serializers
from apps.events.models import Event
from apps.societies.models import Society

class EventSerializer(serializers.ModelSerializer):
    """Serializer for the Event model"""

    start_datetime = serializers.SerializerMethodField()
    end_datetime = serializers.SerializerMethodField()
    event_type = serializers.SerializerMethodField()

    society = serializers.PrimaryKeyRelatedField(
        queryset=Society.objects.all(),
        many=True,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Event
        fields = '__all__'

    def get_start_datetime(self, obj):
        """Format start datetime correctly"""
        return f"{obj.date.strftime('%Y-%m-%d')}T{obj.start_time.strftime('%H:%M:%S')}"
    
    def get_end_datetime(self, obj):
        """Format end datetime correctly"""
        if obj.end_time:
            return f"{obj.date.strftime('%Y-%m-%d')}T{obj.end_time.strftime('%H:%M:%S')}"
        return None 

    def get_event_type(self, obj):
        event_choices = dict(obj._meta.get_field('event_type').choices)
        return event_choices.get(obj.event_type, obj.event_type)
