# wellbeing/urls.py
from django.urls import path
from wellbeing.views import register_view, quiz_view, profile_view

urlpatterns = [
    path("register/", register_view, name="register"),
    path("", quiz_view, name="quiz"),
    path("profile/", profile_view, name="profile"),
]
