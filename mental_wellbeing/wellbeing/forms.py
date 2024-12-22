# wellbeing/forms.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from wellbeing.models import Post

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'image']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Share your thoughts...'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }