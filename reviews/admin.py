from django.contrib import admin
from .models import Movie, Review, Genre

# Регистрация моделей
admin.site.register(Movie)
admin.site.register(Review)
admin.site.register(Genre)

class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'get_genres') # Столбцы в списке
    filter_horizontal = ('genres',) # Удобный интерфейс выбора жанров (виджет "стрелочки")

    # Вспомогательный метод, чтобы видеть жанры прямо в списке фильмов
    def get_genres(self, obj):
        return ", ".join([g.name for g in obj.genres.all()])
    get_genres.short_description = 'Жанры'

# Если Movie уже был зарегистрирован просто через admin.site.register(Movie),
# сначала удали старую строку или замени на эту:
admin.site.unregister(Movie) # Снимаем старую регистрацию, если она была
admin.site.register(Movie, MovieAdmin) # Регистрируем с новыми настройками