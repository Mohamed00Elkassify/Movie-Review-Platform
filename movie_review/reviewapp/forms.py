from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Rating

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class RatingForm(forms.ModelForm):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Share your thoughts about this movie... What did you like or dislike?',
            'style': 'background: rgba(42, 42, 42, 0.85); border: 1px solid #666; color: #d8d8d8; border-radius: 8px;'
        }),
        required=False,
        label="Your Review"
    )
    
    class Meta:
        model = Rating
        fields = ['stars', 'comment']