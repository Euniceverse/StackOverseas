from django.conf import settings
from apps.societies.models import Society
from django.db import models
from django.utils import timezone
from datetime import timedelta


from config.constants import MAX_DESCRIPTION
import os

#ranking
class MemberRating(models.Model):
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='rank')
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1000)

    class Meta:
        unique_together = ('society', 'member')
        ordering = ['-rating']

    def __str__(self):
        full_name = f"{self.member.first_name} {self.member.last_name}".strip()
        return f"{full_name or self.member.email} — {self.rating} pts"


class Match(models.Model):
    society = models.ForeignKey(Society, on_delete=models.CASCADE)
    player1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_as_p1')
    player2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_as_p2')
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_wins', null=True, blank=True)
    player1_delta = models.IntegerField(default=0)
    player2_delta = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        p1 = f"{self.player1.first_name} {self.player1.last_name}".strip() or self.player1.email
        p2 = f"{self.player2.first_name} {self.player2.last_name}".strip() or self.player2.email
        win = f"{self.winner.first_name} {self.winner.last_name}".strip() if self.winner else 'Draw'
        return f"{p1} vs {p2} — Winner: {win}"


class HallOfFame(models.Model):
    society = models.ForeignKey(Society, on_delete=models.CASCADE)
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    season = models.CharField(max_length=20)  # e.g. "2025-Q1", "2024-Winter"
    highest_rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('society', 'season')

    def __str__(self):
        name = f"{self.member.first_name} {self.member.last_name}".strip() or self.member.email
        return f"{name} - {self.season} ({self.highest_rating} pts)"

#comment
class Comment(models.Model):
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_comments', blank=True)

    def __str__(self):
        return f"{self.author.username} @ {self.society.name}: {self.content[:20]}"

    def total_likes(self):
        return self.likes.count()

#gallery
def gallery_image_path(instance, filename):
    return os.path.join('gallery', f"user_{instance.gallery.society.id}", filename)

class Gallery(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    society = models.ForeignKey(Society, on_delete=models.CASCADE, null=True, blank=True, related_name="gallery_society")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Image(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=gallery_image_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"Image in {self.gallery.title}"
    
#poll
class Poll(models.Model):
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='poll')
    title = models.CharField(max_length=255, default='Untitled Poll')
    description = models.TextField(blank=True)
    deadline = models.DateTimeField(default=timezone.now() + timedelta(days=7))  

    def is_closed(self):
        return timezone.now() > self.deadline

    def __str__(self):
        return f"{self.title} ({self.society.name})"


class Question(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="questions")
    question_text = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=255)
    option_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.question.question_text} - {self.option_text}"
    
class Vote(models.Model):
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    voted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('option', 'voted_by')

    def __str__(self):
        return f"{self.voted_by} voted for {self.option.option_text}"