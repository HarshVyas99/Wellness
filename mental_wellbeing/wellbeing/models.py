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
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    audio = models.FileField(upload_to='posts/audio/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
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
    read = models.BooleanField(default=False)

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
    
from django.contrib.auth.models import User

# Predefined set of interests (for example, hobbies)
INTEREST_CHOICES = [
    ('sports', 'Sports'),
    ('music', 'Music'),
    ('movies', 'Movies'),
    ('technology', 'Technology'),
    ('reading', 'Reading'),
    ('traveling', 'Traveling'),
    ('art', 'Art'),
    ('gaming', 'Gaming'),
]

class Profile(models.Model):
 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    interests = models.CharField(
        max_length=100, 
        choices=INTEREST_CHOICES, 
        blank=True, 
        null=True
    )

    def __str__(self):
        return f"Profile of {self.user.username}"


from django.db import models

class ContactEmail(models.Model):
    email = models.EmailField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
class MentalWellbeingContent(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('article', 'Article'),
        ('self_care_tip', 'Self-care Tip'),
        ('practice', 'Practice'),
        ('resource', 'Resource'),
        ('video', 'Video'),  # Add video content type
    ]
    
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    url = models.URLField(blank=True, null=True)  # URL for video or article link
    description = models.TextField(blank=True, null=True)  # Description for breathing exercises
    video_url=models.URLField(blank=True, null=True)  # URL for video or article link
    video_file = models.FileField(upload_to='meditation_videos/', blank=True, null=True)  # For uploading videos directly
    image = models.ImageField(upload_to='meditation_images/', blank=True, null=True)  # Optional image for breathing exercise
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

from django.db import models
from django.contrib.auth.models import User

class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ('Mood Magic', 'Mood Magic'),
        ('Vibe Guide', 'Vibe Guide'),
        ('Wellness Wingman', 'Wellness Wingman'),
        ('general', 'General Feedback'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    rating = models.IntegerField(default=1)  # 1 to 5 rating
    comments = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username} - {self.category}"
    
class MembershipPlan(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Basic is free
    duration_minutes = models.PositiveIntegerField(default=20)  # Surfing time in minutes
    features = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class UserMembership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()

    def is_active(self):
        return now() <= self.end_date

    def __str__(self):
        return f"{self.user.username} - {self.membership.name if self.membership else 'No Membership'}"
    
from django.utils.timezone import now

class MembershipUpgradeRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='upgrade_requests')
    requested_plan = models.ForeignKey('MembershipPlan', on_delete=models.CASCADE, related_name='upgrade_requests')
    requested_on = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    processed_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} -> {self.requested_plan.name} on {self.requested_on.strftime('%Y-%m-%d %H:%M:%S')}"