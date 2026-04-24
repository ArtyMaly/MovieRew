from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название жанра")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    poster = models.ImageField(upload_to='movies/', blank=True, null=True)
    release_date = models.DateField()

    genres = models.ManyToManyField(Genre, related_name='movies', verbose_name="Жанры")

    def __str__(self):
        return self.title

    def get_average_rating(self):
        avg_rating = self.reviews.aggregate(Avg('rating'))['rating__avg']
        if avg_rating:
            return round(avg_rating, 1)
        return 0 
    
class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 11)])
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_reviews', blank=True)

    def total_likes(self):
        return self.likes.count()

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie') 

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)

    is_premium = models.BooleanField(default=False, verbose_name="Премиум статус")

    def __str__(self):
        return f'Профиль {self.user.username} ({"Premium" if self.is_premium else "Free"})'