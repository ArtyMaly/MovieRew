from . import views
from django.urls import path
from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie, Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .forms import MovieForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .models import Favorite

def movie_list(request):
    query = request.GET.get('q') # Получаем текст из инпута поиска
    if query:
        # Ищем фильмы, где название содержит query (без учета регистра)
        movies = Movie.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
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

def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    reviews = movie.reviews.all().order_by('-created_at') # Получаем все отзывы к этому фильму
    
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')
            
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie # Привязываем отзыв к текущему фильму
            review.user = request.user # Привязываем к текущему юзеру
            review.save()
            return redirect('movie_detail', pk=movie.pk)
    else:
        form = ReviewForm()

    return render(request, 'reviews/movie_detail.html', {
        'movie': movie,
        'reviews': reviews,
        'form': form
    })

def is_moderator(user):
    return user.is_staff

@user_passes_test(is_moderator)
def add_movie(request):
    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES) # request.FILES обязателен для Pillow!
        if form.is_valid():
            form.save()
            return redirect('movie_list')
    else:
        form = MovieForm()
    return render(request, 'reviews/add_movie.html', {'form': form})

@user_passes_test(is_moderator)
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    movie_pk = review.movie.pk
    review.delete()
    return redirect('movie_detail', pk=movie_pk)

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    
    if review.user == request.user or request.user.is_staff:
        movie_pk = review.movie.pk
        review.delete()
        return redirect('movie_detail', pk=movie_pk)
    else:
        raise PermissionDenied

@login_required
def profile(request):
    # Получаем все избранные фильмы пользователя
    favorites = Favorite.objects.filter(user=request.user).select_related('movie')
    # Также можно получить все отзывы пользователя
    user_reviews = Review.objects.filter(user=request.user).select_related('movie')
    
    return render(request, 'reviews/profile.html', {
        'favorites': favorites,
        'user_reviews': user_reviews
    })

@login_required
def toggle_favorite(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)
    
    if not created:
        favorite.delete() # Если уже было в избранном — удаляем
    
    return redirect(request.META.get('HTTP_REFERER', 'movie_detail'))