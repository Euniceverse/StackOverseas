from django.test import TestCase
from django.utils import timezone
from apps.events.models import Event
from apps.events.serializers import EventSerializer
from datetime import time
from decimal import Decimal

class EventSerializerTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name="SerializeMe",
            description="desc",
            date=timezone.now(),
            start_time=time(9, 30),
            end_time=time(11, 0),
            event_type="sports",
            keyword="fun",
            location="Campus",
            capacity=100,
            fee=Decimal("0.00"),
            is_free=True
        )

    def test_serialization(self):
        serializer = EventSerializer(self.event)
        data = serializer.data
        self.assertIn("id", data)
        self.assertEqual(data["name"], "SerializeMe")
        # Check our get_start_datetime() logic
        self.assertTrue(data["start_datetime"].endswith("09:30:00"))
        self.assertTrue(data["end_datetime"].endswith("11:00:00"))
        # Check event_type label is returned
        self.assertEqual(data["event_type"], "Sports")  # from your get_event_type override

    def test_deserialization(self):
        payload = {
            "name": "New Name",
            "description": "New desc",
            "date": timezone.now().isoformat(),
            "event_type": "sports",
            "keyword": "keyword",
            "location": "New Loc",
            "latitude": 0.0,
            "longitude": 0.0,
            "fee": "0.00",
            "is_free": True,
            "society": []
        }
        ser = EventSerializer(data=payload)
        self.assertTrue(ser.is_valid(), ser.errors)
        new_obj = ser.save()
        self.assertEqual(new_obj.name, "New Name")