from django.db import models
from django.utils import timezone
from apps.events.models import Event

class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    society = models.CharField(max_length=100)
    date_posted = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="news_images/", blank=True, null=True)
    is_published = models.BooleanField(default=False)
    event = models.ForeignKey("events.Event", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.title
