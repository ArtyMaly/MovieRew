from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Q
from django.core.paginator import Paginator
from .models import Movie, Review, Favorite, Genre, Profile
from .forms import ReviewForm, MovieForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm

# --- ГЛАВНАЯ СТРАНИЦА (Поиск + Слайдер) ---
def movie_list(request):
    # 1. Сбор параметров из GET-запроса
    genre_id = request.GET.get('genre')
    query = request.GET.get('q')
    sort = request.GET.get('sort')
    year = request.GET.get('year')

    # 2. Базовый запрос с расчетом среднего рейтинга
    movies_listing = Movie.objects.annotate(avg_rating=Avg('reviews__rating'))

    # 3. ФИЛЬТРАЦИЯ (теперь фильтры могут суммироваться)
    if genre_id:
        movies_listing = movies_listing.filter(genres__id=genre_id)
    
    if query:
        movies_listing = movies_listing.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        
    if year:
        movies_listing = movies_listing.filter(release_date__year=year)

    # 4. СОРТИРОВКА
    if sort == 'rating':
        movies_listing = movies_listing.order_by('-avg_rating') # От высокого к низкому
    elif sort == 'newest':
        movies_listing = movies_listing.order_by('-release_date') # Сначала свежие
    elif sort == 'oldest':
        movies_listing = movies_listing.order_by('release_date') # Сначала ретро
    else:
        movies_listing = movies_listing.order_by('-id') # По умолчанию: последние добавленные

    # 5. ДАННЫЕ ДЛЯ СЛАЙДЕРА (Топ-5 по рейтингу)
    carousel_movies = Movie.objects.annotate(avg_rating=Avg('reviews__rating')).filter(
        avg_rating__isnull=False
    ).order_by('-avg_rating')[:5]

    # 6. Список уникальных годов для выпадающего списка в шаблоне
    years = Movie.objects.dates('release_date', 'year', order='DESC')

    return render(request, 'reviews/movie_list.html', {
        'movies': movies_listing,
        'genres': Genre.objects.all(),
        'years': [y.year for y in years], # Список годов: [2024, 2023, ...]
        'carousel_movies': carousel_movies
    })

# --- СТРАНИЦА ФИЛЬМА (Сохранение отзыва + Пагинация) ---
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    reviews = movie.reviews.all().order_by('-user__profile__is_premium', '-created_at')

    similar_movies = Movie.objects.filter(genres__in=movie.genres.all()).exclude(pk=movie.pk).distinct()[:4]
    
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
        'similar_movies': similar_movies,
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
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Ваш профиль обновлен!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        # Проверяем, есть ли профиль, если нет — создаем (для старых юзеров)
        p_form, created = Profile.objects.get_or_create(user=request.user)
        p_form = ProfileUpdateForm(instance=p_form)

    favorites = Favorite.objects.filter(user=request.user).select_related('movie')
    user_reviews = Review.objects.filter(user=request.user).select_related('movie')
    
    return render(request, 'reviews/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
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

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Чтобы сессия не слетела
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {'form': form})

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