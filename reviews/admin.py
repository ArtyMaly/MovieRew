from django.contrib import admin
from .models import Movie, Review, Genre, Profile, Collection


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

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_premium') 
    list_filter = ('is_premium',)        
    search_fields = ('user__username',)  

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    filter_horizontal = ('movies',)