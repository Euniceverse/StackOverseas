from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from apps.events.models import Event, Host
from apps.news.models import News

@receiver(post_save, sender=Event)
def create_news_on_event(sender, instance, created, **kwargs):
    """Automatically create a news article when an event is created."""
    if created: 
        host_societies = Host.objects.filter(event=instance).select_related("society")

        for host in host_societies:
            News.objects.create(
                title=f"New Event: {instance.name}",
                content=f"New Event on {instance.date.strftime('%B %d, %Y')}. Hosted by {host.society.name}.",
                society=host.society, 
                date_posted=now(),
                is_published=True  
            )
