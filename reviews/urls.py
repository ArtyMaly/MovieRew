from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('register/', views.register, name='register'),
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('movie/add/', views.add_movie, name='add_movie'),
    path('review/<int:pk>/delete/', views.delete_review, name='delete_review'),
    path('profile/', views.profile, name='profile'),
    path('movie/<int:movie_pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('review/<int:pk>/like/', views.like_review, name='like_review'),
    path('review/<int:pk>/edit/', views.edit_review, name='edit_review'),
]