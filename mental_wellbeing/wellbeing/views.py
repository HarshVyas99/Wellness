# wellbeing/views.py
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from wellbeing.models import Recommendation, QuizResponse, Post, Conversation, Message, UserQuizResult, ContactEmail, MentalWellbeingContent
from wellbeing.forms import RegistrationForm, PostForm, ProfileForm, ContactEmailForm
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from wellbeing.utils import get_or_create_conversation, get_active_doctors
import re
from django.utils.timezone import now
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator
from datetime import timedelta

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

def register_view(request):
    if request.method == 'POST':
        user_form = RegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user_profile = profile_form.save(commit=False)
            user_profile.user = user
            user_profile.save()

            login(request, user)  # Automatically log in the user after registration
            return redirect('about_us')  # Redirect to the profile page (you can customize this)
    else:
        user_form = RegistrationForm()
        profile_form = ProfileForm()

    return render(request, 'wellbeing/register.html', {'user_form': user_form, 'profile_form': profile_form})

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
    profile = request.user.profile  # Assuming user has a related Profile model
    user_quiz_results = UserQuizResult.objects.filter(user=request.user)
    # Check if the user is in edit mode
    is_edit_mode = request.GET.get('edit', False)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)  # Pass the existing profile as instance
        if form.is_valid():
            form.save()  # Save the updated profile
            return redirect('profile')  # Redirect to the same page after saving
    else:
        form = ProfileForm(instance=profile)  # Prepopulate the form with the current profile data

    user_feedback = Feedback.objects.filter(user=request.user)
    user_membership = getattr(request.user, 'usermembership', None)
    remaining_time = None
    if user_membership and user_membership.membership.name == 'basic':
        remaining_time = max(user_membership.end_date - now(), timedelta(0))  # Ensure non-negative
    return render(request, 'wellbeing/profile.html', {'user_quiz_results': user_quiz_results, 'profile': profile, 'form': form, 'is_edit_mode': is_edit_mode, 'user_feedback': user_feedback, 'user_membership': user_membership, 'remaining_time': remaining_time})


@login_required
def feed_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed')  # Redirect to the same page after submission
    else:
        form = PostForm()

    # Fetch all posts for the feed
    posts = Post.objects.all().order_by('-created_at')  # Latest posts first

    return render(request, 'wellbeing/feed.html', {'form': form, 'posts': posts})

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
        return render(request, "wellbeing/take_quiz.html")
 
def about_us(request):
    return render(request, 'wellbeing/about_us.html')

@login_required
def online_users(request):
    # Get all users except the logged-in user
    users = User.objects.exclude(id=request.user.id)

    # Get unread messages for the logged-in user
    unread_messages = Message.objects.filter(conversation__participants=request.user, read=False)
    unread_count = unread_messages.count()

    return render(request, 'wellbeing/chats/online_users.html', {
        'users': users,
        'unread_count': unread_count,
    })
    
@login_required
def start_user_conversation(request, user_id):
    # Get the user to start a conversation with
    other_user = get_object_or_404(User, id=user_id)
    # Check if a conversation already exists between the logged-in user and the other user
    conversation, created = get_or_create_conversation([request.user.id,user_id])
    # Mark all unread messages in this conversation as read
    conversation.messages.filter(read=False).update(read=True)
    messages = conversation.messages.order_by('timestamp')
    return render(request, 'wellbeing/chats/conversation.html', {'conversation': conversation, 'messages': messages})

@login_required
def user_conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    conversation.messages.filter(read=False).update(read=True)
    messages = conversation.messages.order_by('timestamp')
    return render(request, 'wellbeing/chats/conversation.html', {'conversation': conversation, 'messages': messages})


@login_required
def user_inbox(request):
    # Get all conversations the logged-in user is part of
    conversations = Conversation.objects.filter(participants=request.user)

    # Get the latest message for each conversation
    conversations_with_last_message = []
    for conversation in conversations:
        last_message = conversation.messages.order_by('-timestamp').first()
        conversations_with_last_message.append({
            'conversation': conversation,
            'last_message': last_message,
            'unread_count': conversation.messages.filter(read=False).count(),
        })

    return render(request, 'wellbeing/chats/user_inbox.html', {
        'conversations_with_last_message': conversations_with_last_message,
    })
    
def contact_view(request):
    if request.method == 'POST':
        form = ContactEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Save to database (optional)
            ContactEmail.objects.create(email=email)

            # Send email
            send_mail(
                subject='Zenvibe: Thank you for contacting us!',
                # If you have any doubt or queries please call us at.
                message=f'''We will get back to you soon.
                If you have any doubt or queries please contact us at {settings.SUPPORT_NUMBER}.
                ''' ,
                from_email='Zenvibe Admin Account <zenvibeadmin@gmail.com>',
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, "Email submitted successfully. Check your inbox for further updates!")
            return redirect('about_us')    
    else:
        form = ContactEmailForm()

    return render(request, 'wellbeing/contact_us.html', {'form': form})

def disclaimer_view(request):
    return render(request, 'wellbeing/disclaimer.html')

@login_required
def wellbeing_content_page(request):
    # Get query parameters for search, filter, and sort
    search_query = request.GET.get('search', None)
    content_type_filter = request.GET.get('content_type', None)
    sort_by = request.GET.get('sort_by', None)  # Default sorting by title
    
    # Filter content based on the query parameters
    content = MentalWellbeingContent.objects.all()
    
    if search_query:
        content = content.filter(title__icontains=search_query) | content.filter(description__icontains=search_query)
    
    if content_type_filter:
        content = content.filter(content_type=content_type_filter)
    
    # Sorting
    if sort_by == 'title':
        content = content.order_by('title')
    elif sort_by == 'content_type':
        content = content.order_by('title')
    elif sort_by == 'date':
        content = content.order_by('-created_at')  # Assuming you have a created_at field
    else:
        content = content.order_by('-created_at')  # Assuming you have a created_at field
    
    if search_query is not None or content_type_filter is not None or sort_by is not None:
        show_clear_filter=True
    else:
        show_clear_filter=False
        
    # Pagination setup
    paginator = Paginator(content, 20)  # Show 20 articles per page
    page_number = request.GET.get('page')  # Get the current page number from the GET request
    page_obj = paginator.get_page(page_number)  # Get the content for the current page
        

    return render(request, 'wellbeing/wellbeing_content.html', {
        'wellbeing_content': page_obj,
        'search_query': search_query,
        'content_type_filter': content_type_filter,
        'sort_by': sort_by,
        'show_clear_filter':show_clear_filter,
    })
    
from wellbeing.forms import FeedbackForm
from wellbeing.models import Feedback

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user  # Associate feedback with the logged-in user
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('about_us')  # Redirect to a relevant page, e.g., homepage
    else:
        form = FeedbackForm()
    
    return render(request, 'wellbeing/submit_feedback.html', {'form': form})

@login_required
def view_feedback(request):
    feedback_list = Feedback.objects.all().order_by('-submitted_at')  # Show the latest feedback first
    return render(request, 'wellbeing/admin_feedback.html', {'feedback_list': feedback_list})

from .models import MembershipUpgradeRequest, MembershipPlan
from .forms import MembershipUpgradeRequestForm

@login_required
def request_upgrade(request):
    user_membership = getattr(request.user, 'usermembership', None)

    # Ensure the user has an active membership
    if not user_membership:
        messages.error(request, "You do not have an active membership.")
        return redirect('about_us')

    if request.method == 'POST':
        form = MembershipUpgradeRequestForm(request.POST)
        if form.is_valid():
            requested_plan = form.cleaned_data['requested_plan']
            notes = form.cleaned_data['notes']

            # Prevent duplicate requests for the same plan
            existing_request = MembershipUpgradeRequest.objects.filter(
                user=request.user,
                requested_plan=requested_plan,
                is_approved=False
            ).first()
            if existing_request:
                messages.info(request, "You already have a pending upgrade request for this plan.")
                return redirect('profile')

            # Create the upgrade request
            MembershipUpgradeRequest.objects.create(
                user=request.user,
                requested_plan=requested_plan,
                notes=notes
            )
            messages.success(request, "Your membership upgrade request has been submitted.")
            return redirect('profile')
    else:
        form = MembershipUpgradeRequestForm()

    return render(request, 'wellbeing/request_upgrade.html', {'form': form})

def view_upgrade_requests(request):
    requests = MembershipUpgradeRequest.objects.filter(is_approved=False).order_by('-requested_on')
    return render(request, 'wellbeing/view_upgrade_requests.html', {'requests': requests})