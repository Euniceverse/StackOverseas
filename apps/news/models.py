from django.db import models
from django.utils import timezone
from django.apps import apps

def upload_to(instance, filename):
    """Save images inside config/media/news_images/ with a unique timestamp."""
    return f"news_images/{timezone.now().strftime('%Y%m%d%H%M%S')}_{filename}"

class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    society = models.CharField(max_length=100)
    date_posted = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)
    is_published = models.BooleanField(default=False)
    
    def get_event(self):
        Event = apps.get_model("events", "Event")
        return Event.objects.filter(news=self)
        
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_posted']