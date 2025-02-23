from django.db import models
from django.conf import settings

class Payment(models.Model):
    PAYMENT_FOR_CHOICES = [
        ("society", "Society"),
        ("event", "Event"),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("paid", "Paid")])
    stripe_charge_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_for = models.CharField(max_length=10, choices=PAYMENT_FOR_CHOICES)

    def __str__(self):
        return f"Payment {self.id} - {self.status} ({self.payment_for})"