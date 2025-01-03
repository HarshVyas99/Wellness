# wellbeing/forms.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from wellbeing.models import Post, Profile, INTEREST_CHOICES, Feedback
from django.core.exceptions import ValidationError


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        

class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'birthdate', 'interests']
        widgets={
            'profile_picture':forms.ClearableFileInput(attrs={
                'class': 'form-control-file', 
                'accept': 'image/*'}),
            'bio':forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...',}),
            'birthdate':forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',}),
            'interests':forms.Select(attrs={
                    'class': 'form-control',
                }) 
        }

        
        


class PostForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label = field.label.capitalize()
            field.widget.attrs.update({'class': 'form-control'})
    class Meta:
        model = Post
        fields = ['text', 'image', 'audio', 'video']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your thoughts here...',
                'rows': 3,
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/jpeg,image/png,image/gif',  # Restrict file types for images
            }),
            'audio': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'audio/mpeg,audio/mp3,audio/wav',  # Restrict file types for audio
            }),
            'video': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'video/mp4,video/mpeg,video/avi,video/webm',  # Restrict file types for video
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text')
        image = cleaned_data.get('image')
        audio = cleaned_data.get('audio')
        video = cleaned_data.get('video')

        # Ensure at least one field is provided
        if not (text or image or audio or video):
            raise ValidationError('Please provide at least one type of content.')

        # Validate file formats
        if image:
            self.validate_image_format(image)
        if audio:
            self.validate_audio_format(audio)
        if video:
            self.validate_video_format(video)

        return cleaned_data

    def validate_image_format(self, image):
        valid_image_types = ['image/jpeg', 'image/png', 'image/gif']
        if image.content_type not in valid_image_types:
            raise ValidationError('Unsupported image format. Only JPEG, PNG, and GIF are allowed.')

    def validate_audio_format(self, audio):
        valid_audio_types = ['audio/mpeg', 'audio/mp3', 'audio/wav']
        if audio.content_type not in valid_audio_types:
            raise ValidationError('Unsupported audio format. Only MP3, WAV, and MPEG audio files are allowed.')

    def validate_video_format(self, video):
        valid_video_types = ['video/mp4', 'video/mpeg', 'video/avi', 'video/webm']
        if video.content_type not in valid_video_types:
            raise ValidationError('Unsupported video format. Only MP4, MPEG, AVI, and WebM video files are allowed.')



class ContactEmailForm(forms.Form):
    email = forms.EmailField(
        label="Your Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['category', 'rating', 'comments']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

from wellbeing.models import MembershipPlan

class MembershipForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset=MembershipPlan.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None,
        label="Choose a Plan"
    )
    

class MembershipUpgradeRequestForm(forms.Form):
    requested_plan = forms.ModelChoiceField(
        queryset=MembershipPlan.objects.exclude(name='basic'),
        label="Choose Plan",
        widget=forms.Select(attrs={'class': 'form-control'})
    )