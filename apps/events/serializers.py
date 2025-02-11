from rest_framework import serializers
from apps.events.models import Event

class EventSerializer(serializers.ModelSerializer):
    start_datetime = serializers.SerializerMethodField() 
    end_datetime = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            "id", "name", "description", "date", "start_time", "end_time",
            "start_datetime", "end_datetime",
            "event_type", "location", "fee", "is_free"
        ]

    def get_start_datetime(self, obj):
        """Format start datetime for frontend calendars"""
        return f"{obj.date}T{obj.start_time}"

    def get_end_datetime(self, obj):
        """Format end datetime if available, else return start datetime"""
        if obj.end_time:
            return f"{obj.date}T{obj.end_time}"
        return f"{obj.date}T{obj.start_time}"