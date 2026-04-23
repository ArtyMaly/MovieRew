from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Q
from django.core.paginator import Paginator

from .models import Movie, Review, Favorite
from .forms import ReviewForm, MovieForm

# --- ГЛАВНАЯ СТРАНИЦА (Поиск + Слайдер) ---
def movie_list(request):
    query = request.GET.get('q')
    
    # Добавляем средний рейтинг к каждому фильму
    movies_annotated = Movie.objects.annotate(avg_rating=Avg('reviews__rating'))

    if query:
        movies_listing = movies_annotated.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        movies_listing = movies_annotated.all()

    # Топ-5 фильмов для слайдера
    carousel_movies = movies_annotated.filter(avg_rating__isnull=False).order_by('-avg_rating')[:5]

    return render(request, 'reviews/movie_list.html', {
        'movies': movies_listing,
        'carousel_movies': carousel_movies
    })

# --- СТРАНИЦА ФИЛЬМА (Сохранение отзыва + Пагинация) ---
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    
    # Обработка отправки отзыва
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')
            
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie 
            review.user = request.user
            review.save()
            return redirect('movie_detail', pk=movie.pk)
    else:
        form = ReviewForm()

    # Пагинация отзывов
    all_reviews = movie.reviews.all().order_by('-created_at')
    paginator = Paginator(all_reviews, 10) # 10 отзывов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'reviews/movie_detail.html', {
        'movie': movie,
        'page_obj': page_obj, 
        'form': form
    })

# --- АККАУНТ И РЕГИСТРАЦИЯ ---
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

@login_required
def profile(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('movie')
    user_reviews = Review.objects.filter(user=request.user).select_related('movie')
    
    return render(request, 'reviews/profile.html', {
        'favorites': favorites,
        'user_reviews': user_reviews
    })

# --- ДЕЙСТВИЯ ПОЛЬЗОВАТЕЛЯ (Лайки, Избранное, Редактирование) ---
@login_required
def toggle_favorite(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        favorite.delete()
    return redirect(request.META.get('HTTP_REFERER', 'movie_detail'))

@login_required
def like_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.likes.filter(id=request.user.id).exists():
        review.likes.remove(request.user) 
    else:
        review.likes.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'movie_detail'))

@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user:
        raise PermissionDenied

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('movie_detail', pk=review.movie.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'reviews/edit_review.html', {'form': form, 'movie': review.movie})

# --- АДМИН-ФУНКЦИИ ---
def is_moderator(user):
    return user.is_staff

@user_passes_test(is_moderator)
def add_movie(request):
    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()
            return redirect('movie_list')
    else:
        form = MovieForm()
    return render(request, 'reviews/add_movie.html', {'form': form})

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    # Удалить может автор или модератор
    if review.user == request.user or request.user.is_staff:
        movie_pk = review.movie.pk
        review.delete()
        return redirect('movie_detail', pk=movie_pk)
    else:
        raise PermissionDenied