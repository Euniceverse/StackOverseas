from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Society(models.Model):
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    society_type = models.CharField(max_length=100)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    membership_request_required = models.BooleanField(default=False)
    
    
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Check whether this society is approved and can be customise
    def is_customisable(self):
        return self.status == 'approved'

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"