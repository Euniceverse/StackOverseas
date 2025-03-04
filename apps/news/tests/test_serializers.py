
from django.test import TestCase
from django.utils import timezone
from rest_framework import serializers
from apps.news.models import News
from apps.societies.models import Society

class DummyNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

class NewsSerializerTests(TestCase):
    def setUp(self):
        self.society = Society.objects.create(
            name="Serialization Society",
            description="Testing serializer coverage",
            society_type="academic",
            manager_id=999,  # or create a real User if needed
            status="approved"
        )
        self.news_item = News.objects.create(
            title="Serialize This",
            content="Testing the serializer.",
            society=self.society,
            date_posted=timezone.now(),
            is_published=False,
            views=10
        )

    def test_serializer_output(self):
        """Check basic serialization of a News object."""
        serializer = DummyNewsSerializer(self.news_item)
        data = serializer.data
        self.assertEqual(data["title"], "Serialize This")
        self.assertEqual(data["content"], "Testing the serializer.")
        self.assertFalse(data["is_published"])
        self.assertEqual(data["views"], 10)

    def test_serializer_input(self):
        """Check that deserialization can work (if you allow create/update)."""
        payload = {
            "title": "New Title",
            "content": "New Content",
            "society": self.society.id,
            "is_published": True,
            "views": 99
        }
        serializer = DummyNewsSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()
        self.assertEqual(obj.title, "New Title")
        self.assertTrue(obj.is_published)
        self.assertEqual(obj.views, 99)