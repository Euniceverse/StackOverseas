from django.db import models
from apps.societies.models import Society 
from config.constants import WIDGET_TYPES

class Widget(models.Model):
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name="widgets")
    widget_type = models.CharField(max_length=50, choices=WIDGET_TYPES)
    position = models.PositiveIntegerField(default=0) 
    custom_html = models.TextField(blank=True, null=True) 

    class Meta:
        ordering = ["position"]
        
    def __str__(self):
        return f"{self.get_widget_type_display()} for {self.society.name}"
