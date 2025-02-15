from rest_framework import serializers
from apps.events.models import Event

class EventSerializer(serializers.ModelSerializer):
    start_datetime = serializers.SerializerMethodField()
    end_datetime = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_start_datetime(self, obj):
        return f"{obj.date}T{obj.start_time}"
    
    def get_end_datetime(self, obj):
        if obj.end_time:
            return f"{obj.date}T{obj.start_time}"
        return f"{obj.date}T{obj.start_time}"
