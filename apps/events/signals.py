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
                is_published=False,
                event=instance # linked to Event  
            )

@receiver(post_save, sender=Event)
def create_auto_news(sender, instance, created, **kwargs):

    if created:
        # For each society hosting the event (in case you allow multiple):
        for soc in instance.society.all():
            News.objects.create(
                event=instance,
                title=f"Auto News for {instance.name}",
                content=f"This was auto-created for {instance.name} in {soc.name}.",
                is_published=False  # Remains unpublished until user edits
            )