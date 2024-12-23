# wellbeing/models.py
from django.db import models
from django.utils.timezone import now
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


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"
    

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation between {', '.join([user.username for user in self.participants.all()])}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"


from django.db import models

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    active_from = models.DateField()  # New field for active date

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    rating = models.IntegerField()  # Rating contributes to the total quiz score

    def __str__(self):
        return self.text

class TempRecommendation(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="recommendations")
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    text = models.TextField()

    def __str__(self):
        return f"Quiz: {self.quiz.title} | {self.min_score}-{self.max_score}"


# Model for UserQuizResult
class UserQuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name='user_results', on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    recommendations = models.ManyToManyField(TempRecommendation, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} (Score: {self.score})"