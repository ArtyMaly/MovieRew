from django import forms
from .models import Review
from .models import Movie, Genre
from django.contrib.auth.models import User
from .models import Profile

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating'] 
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Поделитесь впечатлениями...'}),
        }

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'poster', 'release_date', 'genres']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'genres': forms.CheckboxSelectMultiple(),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']