from . import views
from django.urls import path
from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie, Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'reviews/movie_list.html', {'movies': movies})

def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    return render(request, 'reviews/movie_detail.html', {'movie': movie})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('movie_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})