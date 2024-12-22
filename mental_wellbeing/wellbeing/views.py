# wellbeing/views.py
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from wellbeing.models import Recommendation, QuizResponse, Post, Conversation, Message, UserQuizResult
from wellbeing.forms import RegistrationForm, PostForm
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from wellbeing.utils import get_or_create_conversation, get_active_doctors
import re
from django.utils.timezone import now

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
            return redirect("quiz_for_today")
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
    user_quiz_results = UserQuizResult.objects.filter(user=request.user)
    return render(request, 'wellbeing/profile.html', {'user_quiz_results': user_quiz_results})


@login_required
def feed_view(request):
    posts = Post.objects.all().order_by('-created_at')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'wellbeing/feed.html', {'posts': posts, 'form': form})

@login_required
def active_doctors(request):
    doctors = get_active_doctors()
    return render(request, 'wellbeing/chats/active_doctors.html', {'doctors': doctors})


@login_required
def conversation_detail(request, doctor_id):
    doctor = get_object_or_404(User, id=doctor_id)
    # Fetch or create a conversation
    conversation, created = get_or_create_conversation([request.user.id,doctor_id])
    # conversation, created = Conversation.objects.get_or_create(
    #     participants__in=[doctor,request.user]
    # )
    messages = conversation.messages.order_by('timestamp')
    return render(request, 'wellbeing/chats/conversation.html', {'conversation': conversation, 'messages': messages})

@login_required
def client_conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user not in conversation.participants.all():
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    messages = conversation.messages.order_by('timestamp')  # Fetch messages in chronological order
    return render(request, 'wellbeing/chats/conversation.html', {
        'conversation': conversation,
        'messages': messages,
    })



@login_required
def send_message(request, conversation_id):
    if request.method == 'POST':
        request_data= json.loads(request.body.decode('utf-8'))
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in conversation.participants.all():
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

        content = request_data.get('message')
        if content:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            return JsonResponse({'status': 'success', 'message': message.content, 'timestamp': message.timestamp})
    return JsonResponse({'status': 'error'})

@login_required
def doctor_conversations(request):
    if not request.user.groups.filter(name='Doctors').exists():
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    conversations = Conversation.objects.filter(participants=request.user)
    return render(request, 'wellbeing/chats/doctor_conversations.html', {'conversations': conversations})

@login_required
def doctor_inbox(request):
    if not request.user.groups.filter(name='Doctors').exists():
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    # Fetch conversations involving the doctor
    conversations = Conversation.objects.filter(participants=request.user).order_by('-created_at')

    # Extract user details for display
    user_conversations = [
        {
            'id': conversation.id,
            'user': conversation.participants.exclude(id=request.user.id).first(),  # Get the user (non-doctor participant)
            'last_updated': conversation.created_at,
        }
        for conversation in conversations
    ]

    return render(request, 'wellbeing/chats/doctor_inbox.html', {'user_conversations': user_conversations})

@login_required
def chat_page(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    return render(request, 'wellbeing/chats/chat_page.html', {
        'conversation': conversation,
        'user': request.user,
    })

@login_required
def fetch_messages(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    last_message_id = request.GET.get('last_message_id', 0)
    messages = conversation.messages.filter(id__gt=last_message_id).order_by('timestamp')
    message_list = [
        {
            'id': message.id,
            'sender': message.sender.username,
            'text': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for message in messages
    ]
    return JsonResponse({'messages': message_list})



from django.shortcuts import render
from django.http import JsonResponse
from wellbeing.models import Quiz, Question, Option, TempRecommendation

@login_required
def create_quiz_page(request):
    return render(request, "wellbeing/create_quiz.html")

@login_required
def save_quiz(request):
    if request.method == "POST":
        data = request.POST
        quiz_title = data.get("quiz_title")
        active_from = data.get("active_from")
            
        # Create the Quiz
        quiz = Quiz.objects.create(title=quiz_title,active_from=active_from)

        # Process Questions and Options
        question_count = int(data.get("question_count"))
        for i in range(1, question_count + 1):
            question_text = data.get(f"question_{i}_text")
            question = Question.objects.create(quiz=quiz, text=question_text)
            
            option_count = int(data.get(f"question_{i}_option_count"))
            for j in range(1, option_count + 1):
                option_text = data.get(f"question_{i}_option_{j}_text")
                option_rating = int(data.get(f"question_{i}_option_{j}_rating"))
                Option.objects.create(question=question, text=option_text, rating=option_rating)

        # Process Recommendations
        recommendation_count = int(data.get("recommendation_count"))
        for i in range(1, recommendation_count + 1):
            min_score = int(data.get(f"recommendation_{i}_min_score"))
            max_score = int(data.get(f"recommendation_{i}_max_score"))
            recommendation_text = data.get(f"recommendation_{i}_text")
            TempRecommendation.objects.create(quiz=quiz, min_score=min_score, max_score=max_score, text=recommendation_text)

        return JsonResponse({"success": True, "message": "Quiz created successfully!"})
    
from django.shortcuts import render
from wellbeing.models import Quiz

@login_required
def take_quiz(request, quiz_id):
    quiz = Quiz.objects.prefetch_related("questions__options").get(id=quiz_id)
    return render(request, "wellbeing/take_quiz.html", {"quiz": quiz})

@login_required
def submit_quiz(request, quiz_id):
    if request.method == "POST":
        quiz = Quiz.objects.prefetch_related("questions__options").get(id=quiz_id)
        total_score = 0

        for question in quiz.questions.all():
            selected_option_id = request.POST.get(f"question_{question.id}")
            selected_option = question.options.get(id=selected_option_id)
            total_score += selected_option.rating

        # Fetch the appropriate recommendation
        recommendation = quiz.recommendations.filter(min_score__lte=total_score, max_score__gte=total_score).first()
        
        # Store the quiz result in UserQuizResult
        result = UserQuizResult.objects.create(user=request.user, quiz=quiz, score=total_score)
        if recommendation:
            result.recommendations.add(recommendation)
        

        return render(request, "wellbeing/quiz_result.html", {
            "quiz": quiz,
            "total_score": total_score,
            "recommendation": recommendation,
        })

from django.shortcuts import render, get_object_or_404
from wellbeing.models import Quiz, Question, Option, Recommendation
from django.views import View

class QuizListView(View):
    def get(self, request):
        quizzes = Quiz.objects.all()  # Get all quizzes from the database
        return render(request, 'wellbeing/quiz_list.html', {'quizzes': quizzes})
    
@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, "wellbeing/edit_quiz.html", {"quiz": quiz})

@login_required
def update_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    if request.method == 'POST':
        # Handle quiz title update
        quiz.title = request.POST.get('quiz_title')
        quiz.active_from = request.POST.get("active_from")
        quiz.save()

        # Processing questions and options using regex
        for key, value in request.POST.items():
            # Regex for question-related data: "question_<question_id>_text"
            match = re.match(r'question_(\d+)_text', key)
            if match:
                question_id = match.group(1)
                question=Question.objects.filter(pk=question_id).first()
                if question:
                    question.text = value
                    question.save()
                else:
                    question=Question.objects.create(text=value,quiz=quiz)

                # Process options for the question
                for option_key, option_value in request.POST.items():
                    option_match = re.match(r'question_{}_option_(\d+)_text'.format(question_id), option_key)
                    if option_match:
                        option_id = option_match.group(1)
                        option=Option.objects.filter(pk=option_id).first()
                        if option:
                            option.text = option_value
                            option.rating = request.POST.get('question_{}_option_{}_rating'.format(question_id, option_id))
                            option.save()
                        else:
                            rating = request.POST.get('question_{}_option_{}_rating'.format(question_id, option_id))
                            option=Option.objects.create(text=value,question=question,rating=rating)

        # Processing recommendations
        for key, value in request.POST.items():
            # Regex for recommendation-related data: "recommendation_<recommendation_id>_min_score"
            match = re.match(r'recommendation_(\d+)_min_score', key)
            if match:
                recommendation_id = match.group(1)
                recommendation=TempRecommendation.objects.filter(pk=recommendation_id).first()
                if recommendation:
                    recommendation.min_score = value
                    recommendation.max_score = request.POST.get('recommendation_{}_max_score'.format(recommendation_id))
                    recommendation.text = request.POST.get('recommendation_{}_text'.format(recommendation_id))
                    recommendation.save()
                else:
                    recommendation_min_score = value
                    recommendation_max_score = request.POST.get('recommendation_{}_max_score'.format(recommendation_id))
                    recommendation_text = request.POST.get('recommendation_{}_text'.format(recommendation_id))
                    recommendation=TempRecommendation.objects.create(min_score=recommendation_min_score,max_score=recommendation_max_score,text=recommendation_text,quiz=quiz)
                    recommendation.save()

        return redirect('take_quiz', quiz_id=quiz.pk)

    return render(request, 'edit_quiz.html', {'quiz': quiz})

@login_required
def quiz_for_today(request):
    today = now().date()
    # Get the quiz active for today or the most recent one before today
    quiz = (
        Quiz.objects.filter(active_from__lte=today)
        .order_by('-active_from')  # Order by the latest active date
        .first()
    )

    if quiz:
        return render(request, "wellbeing/take_quiz.html", {"quiz": quiz})
    else:
        # No quiz available
        return render(request, "wellbeing/take_quiz.html",)