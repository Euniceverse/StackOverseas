from django.db import models
from django.utils import timezone
from django.apps import apps

class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    society = models.CharField(max_length=100)
    date_posted = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="news_images/", blank=True, null=True)
    is_published = models.BooleanField(default=False)
    
    def get_event(self):
            Event = apps.get_model("events", "Event")
            return Event.objects.filter(news=self)
        
    def __str__(self):
        return self.title
