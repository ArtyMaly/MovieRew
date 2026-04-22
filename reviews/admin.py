from django.contrib import admin
from .models import Movie, Review

# Регистрация моделей
admin.site.register(Movie)
admin.site.register(Review)