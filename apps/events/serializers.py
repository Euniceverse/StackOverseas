from rest_framework import serializers
from apps.events.models import Event

class EventSerializer(serializers.ModelSerializer):
    """Serializer for the Event model"""

    start_datetime = serializers.SerializerMethodField()
    end_datetime = serializers.SerializerMethodField()
    event_type = serializers.SerializerMethodField()  # ✅ Fix event_type formatting

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
        return None  # If no end time, return None

    def get_event_type(self, obj):
        """Extract only the label from event_type choices"""
        event_choices = dict(obj._meta.get_field('event_type').choices)
        return event_choices.get(obj.event_type, obj.event_type)  # ✅ Converts ('sports', 'Sports') → 'Sports'
