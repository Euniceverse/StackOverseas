from django.conf import settings
from django.db import models
from config.constants import MAX_DESCRIPTION

class Question(models.Model):
    question_text = models.CharField(max_length=MAX_DESCRIPTION)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=MAX_DESCRIPTION)
    option_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.question.question_text} - {self.option_text}"

class Vote(models.Model):
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    voted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['option', 'voted_by'], name='unique_vote_per_option')
        ]
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.option.save()

    def __str__(self):
        voter = self.voted_by if self.voted_by else "Anonymous"
        return f"{voter} voted for {self.option.option_text}"
