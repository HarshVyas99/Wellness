# wellbeing/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from wellbeing.models import Recommendation, QuizResponse
from wellbeing.forms import RegistrationForm

# Questionnaire and scoring logic
QUESTIONS = [
    {"id": 1, "question": "How are you feeling today?", "choices": [("A", "Very happy"), ("B", "Happy"), ("C", "Neutral"), ("D", "Sad"), ("E", "Very sad")]},
    {"id": 2, "question": "How well did you sleep last night?", "choices": [("A", "Very well"), ("B", "Well"), ("C", "Average"), ("D", "Poorly"), ("E", "Very poorly")]},
    {"id": 3, "question": "How stressed do you feel today?", "choices": [("A", "Not stressed at all"), ("B", "Slightly stressed"), ("C", "Moderately stressed"), ("D", "Stressed"), ("E", "Very stressed")]},
    {"id": 4, "question": "Do you feel energetic or lethargic today?", "choices": [("A", "Very energetic"), ("B", "Energetic"), ("C", "Neutral"), ("D", "Lethargic"), ("E", "Very lethargic")]},
    {"id": 5, "question": "How often have you felt positive emotions this week?", "choices": [("A", "Very often"), ("B", "Often"), ("C", "Sometimes"), ("D", "Rarely"), ("E", "Never")]},
]

CHOICE_SCORES = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}

def calculate_score(responses):
    return sum(CHOICE_SCORES.get(answer, 0) for answer in responses.values())

def get_rating(score):
    if score >= 21:
        return "Excellent"
    elif score >= 16:
        return "Good"
    elif score >= 11:
        return "Average"
    elif score >= 6:
        return "Low"
    return "Very Low"

# User Registration
def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("quiz")
    else:
        form = RegistrationForm()
    return render(request, "wellbeing/register.html", {"form": form})

# Quiz View
@login_required
def quiz_view(request):
    if request.method == "POST":
        responses = {f"q{q['id']}": request.POST.get(f"q{q['id']}") for q in QUESTIONS}
        score = calculate_score(responses)
        rating = get_rating(score)

        # Save the quiz result
        QuizResponse.objects.create(user=request.user, score=score, rating=rating)

        recommendations = Recommendation.objects.filter(rating_category=rating)
        return render(request, "wellbeing/results.html", {"score": score, "rating": rating, "recommendations": recommendations})

    return render(request, "wellbeing/quiz.html", {"questions": QUESTIONS})

# User Profile
@login_required
def profile_view(request):
    responses = QuizResponse.objects.filter(user=request.user).order_by("-date_taken")
    return render(request, "wellbeing/profile.html", {"responses": responses})
