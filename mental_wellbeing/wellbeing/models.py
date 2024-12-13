# wellbeing/models.py
from django.db import models
from django.contrib.auth.models import User

class QuizResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_taken = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField()
    rating = models.CharField(max_length=50)  # e.g., "Excellent", "Good", etc.

    def __str__(self):
        return f"{self.user.username} - {self.date_taken} - {self.rating}"


class Recommendation(models.Model):
    RATING_CHOICES = [
        ("Excellent", "Excellent"),
        ("Good", "Good"),
        ("Average", "Average"),
        ("Low", "Low"),
        ("Very Low", "Very Low"),
    ]

    rating_category = models.CharField(max_length=50, choices=RATING_CHOICES)
    type = models.CharField(max_length=50)  # e.g., "Music", "Article"
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)  # Optional for external resources

    def __str__(self):
        return f"{self.rating_category} - {self.title}"

class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField()
    recommendation = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.score}"
