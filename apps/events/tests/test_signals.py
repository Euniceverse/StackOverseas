
from django.test import TestCase
from django.utils import timezone
from apps.events.models import Event, Host
from apps.societies.models import Society
from apps.news.models import News
from django.conf import settings

class EventSignalsTest(TestCase):
    def setUp(self):
        self.user_mgr = User.objects.create_user(
            email='signal@mgr.ac.uk',
            first_name='Signal',
            last_name='Manager',
            preferred_name='SigMgr',
            password='pass'
        )
        self.soc = Society.objects.create(
            name="SignalSoc",
            manager=user_mgr,
            status="approved",
            society_type="arts"
        )

    def test_create_news_on_event(self):
        """When a new Event is created, each Host triggers a new News item (is_published=False)."""
        # create the event
        event = Event.objects.create(
            name="SignalTestEvent",
            description="desc",
            date=timezone.now(),
            event_type="sports",
            keyword="chess",
            location="London"
        )
        # but signals only run if we also have Host records
        Host.objects.create(event=event, society=self.soc)

        event.save()

        self.assertEqual(News.objects.count(), 0, "No news created because event was not created with host at the same time.")
      
        from django.db.models.signals import post_save
        from apps.events.signals import create_news_on_event

        post_save.send(sender=Event, instance=event, created=True)

        self.assertEqual(News.objects.count(), 1)
        news = News.objects.first()
        self.assertIn("SignalTestEvent", news.title)
        self.assertEqual(news.society, self.soc)
        self.assertFalse(news.is_published)