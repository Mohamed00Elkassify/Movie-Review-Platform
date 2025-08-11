from django.urls import path
from .views import (
    RegisterView,
    MovieListView,
    MovieDetailView,
    SubmitReviewView,
    WatchlistToggleView,
    WatchlistView,
)

urlpatterns = [
    # Auth & registration
    path('signup/', RegisterView.as_view(), name='signup'),

    # Movies
    path('', MovieListView.as_view(), name='movie_list'),
    path('movies/<int:pk>/', MovieDetailView.as_view(), name='movie_detail'),

    # Reviews
    path('movies/<int:pk>/review/', SubmitReviewView.as_view(), name='submit_review'),

    # Watchlist
    path('movies/<int:pk>/watchlist-toggle/', WatchlistToggleView.as_view(), name='watchlist_toggle'),
    path('watchlist/', WatchlistView.as_view(), name='watchlist'),
]