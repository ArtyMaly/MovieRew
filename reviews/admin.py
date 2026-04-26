from django.contrib import admin
from .models import Movie, Review, Genre


admin.site.register(Movie)
admin.site.register(Review)
admin.site.register(Genre)

class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'get_genres') 
    filter_horizontal = ('genres',)


    def get_genres(self, obj):
        return ", ".join([g.name for g in obj.genres.all()])
    get_genres.short_description = 'Жанры'

admin.site.unregister(Movie) 
admin.site.register(Movie, MovieAdmin) 