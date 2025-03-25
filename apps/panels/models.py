from django.conf import settings
from django.db import models
from config.constants import MAX_DESCRIPTION
import os

#gallery
def gallery_image_path(instance, filename):
    """이미지를 저장할 경로 설정: media/gallery/user_{id}/{filename}"""
    return os.path.join('gallery', f"user_{instance.gallery.owner.id}", filename)

class Gallery(models.Model):
    """갤러리 모델 (사용자별 갤러리)"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="galleries")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Image(models.Model):
    """갤러리에 포함된 이미지 모델"""
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=gallery_image_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image in {self.gallery.title}"
#poll
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
