# wellbeing/urls.py
from django.urls import path
from wellbeing import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    # path("", views.quiz_view, name="quiz"),
    path("profile/", views.profile_view, name="profile"),
    path('feed/', views.feed_view, name='feed'),
    path('active-doctors/', views.active_doctors, name='active_doctors'),
    path('conversation/<int:doctor_id>/', views.conversation_detail, name='conversation_detail'),
    path('send-message/<int:conversation_id>/', views.send_message, name='send_message'),
    path('doctor/inbox/', views.doctor_inbox, name='doctor_inbox'),
    path('client-conversation/<int:conversation_id>/', views.client_conversation_detail, name='client_conversation_detail'),
    path('chat/<int:conversation_id>/', views.chat_page, name='chat_page'),
    path('chat/<int:conversation_id>/fetch_messages/', views.fetch_messages, name='fetch_messages'),
    path('quiz/', views.QuizListView.as_view(), name='quiz_list'),  # List of quizzes
    path('quiz/create-quiz/', views.create_quiz_page, name='create_quiz'),
    path('quiz/save-quiz/', views.save_quiz, name='save_quiz'),
    path('quiz/take/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz/submit/<int:quiz_id>/', views.submit_quiz, name='submit_quiz'),
    path('quiz/edit/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),
    path('quiz/update/<int:quiz_id>/', views.update_quiz, name='update_quiz'),
    path('participate/', views.quiz_for_today, name='quiz_for_today'),
    path('', views.about_us, name='about_us'),
]
