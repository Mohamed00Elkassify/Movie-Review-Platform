from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, ListView, DetailView, View
from .forms import RegisterForm, RatingForm
from django.urls import reverse_lazy
from .models import Movie, Rating, Watchlist
from django.db.models import Avg
from datetime import date, timedelta
# Create your views here.

class RegisterView(FormView):
    template_name = 'registration/signup.html'
    form_class = RegisterForm
    succes_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class MovieListView(ListView):
    """
    MovieListView:
    A view to display a paginated list of movies with filtering, searching, and sorting options.
    - Filters: genre, year, rating.
    - Search: by movie title.
    - Sorting: by rating or release date.
    - Context: Includes top-rated movies released this week.
    """
    model = Movie
    context_object_name = 'movies'
    template_name = 'reviewapp/movie_list.html'
    paginate_by = 15

    def get_queryset(self):
        qs = Movie.objects.all()
        genre = self.request.GET.get('genre')
        year = self.request.GET.get('year') 
        rating = self.request.GET.get('rating')         
        query = self.request.GET.get('q')
        sort = self.request.GET.get('sort')

        if query:
            qs = qs.filter(title__icontains=query)
        if genre:
            qs = qs.filter(genres__name__iexact=genre)
        if year:
            qs = qs.filter(release_date__year=year)
        if rating:
            qs = qs.annotate(avg_rating=Avg('rating__stars')).filter(avg_rating__gte=rating)
        if sort == 'rating':
            qs = qs.annotate(avg_rating=Avg('rating__stars')).order_by('-avg_rating')
        elif sort == 'release':
            qs = qs.order_by('-release_date')

        return qs.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        startweek = today - timedelta(days=today.weekday())
        endweek = startweek + timedelta(days=6)
        context['top_picks_this_week'] = (
            Movie.objects.filter(
                release_date__range=(startweek, endweek)
            ).annotate(avg_rating=Avg('rating__stars')).order_by('-avg_rating')[:5]
        )
        return context
    
class MovieDetailView(DetailView):
    """
    View for displaying detailed information about a specific movie, 
    including its reviews, average rating, and user-specific data 
    such as review form and watchlist status.
    """
    model = Movie
    template_name = 'reviewapp/movie_detail.html'
    context_object_name = 'movies'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        reviews = Rating.objects.filter(movie=movie)
        context['reviews'] = reviews
        context['avg_rating'] = reviews.aggregate(Avg('stars')) or 0
        if self.request.user.is_authenticated:
            context['review_form'] = RatingForm(
                instance=Rating.objects.filter(user=self.request.user, movie=movie).first()
            )
            context['in_watchlist'] = Watchlist.objects.filter(user=self.request.user, movie=movie).exists()
        else:
            context['review_form'] = None
            context['in_watchlist'] = False
        
        return context


class SubmitReviewView(LoginRequiredMixin, FormView):
    """
    SubmitReviewView handles the submission of movie reviews by authenticated users.
    This view allows users to submit a rating and comment for a specific movie. If a review
    already exists for the user and movie, it updates the existing review. Otherwise, it creates
    a new review.
    Attributes:
        form_class (RatingForm): The form used to submit the review.
        template_name (str): The template used to render the review submission page.
    Methods:
        form_valid(form):
            Processes the valid form, updates or creates a review, and returns the response.
    """
    form_class = RatingForm
    template_name = 'reviewapp/submit_review.html'

    def form_valid(self, form):
        movie = get_object_or_404(Movie, pk=self.kwargs['pk'])
        existing_review = Rating.objects.filter(user=self.request.user, movie=movie).first()
        if existing_review:
            existing_review.stars = form.cleaned_data['stars']
            existing_review.comment = form.cleaned_data['comment']
            existing_review.save()
        else:
            new_review = Rating(
                user=self.request.user,
                movie=movie,
                stars=form.cleaned_data['stars'],
                comment=form.cleaned_data['comment']
            )
            new_review.save()
        return super().form_valid(form)


class WatchlistToggleview(LoginRequiredMixin, View):
    """
    View to toggle a movie's presence in the user's watchlist.

    If the movie is already in the user's watchlist, it will be removed.
    If the movie is not in the user's watchlist, it will be added.

    Attributes:
        LoginRequiredMixin: Ensures the user is authenticated before accessing the view.
        View: Base class for handling HTTP GET requests.

    Methods:
        get(request, pk): Handles the GET request to toggle the watchlist entry for the specified movie.
    """
    def get(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        existing_entry = Watchlist.objects.filter(user=self.request.user, movie=movie).first()
        if existing_entry:
            existing_entry.delete()
        else:
            Watchlist.objects.create(user=self.request.user, movie=movie)

class WatchlistView(LoginRequiredMixin, ListView):
    """
    View to display the watchlist of movies for the logged-in user.
    Inherits:
        LoginRequiredMixin: Ensures the user is authenticated to access the view.
        ListView: Provides a list-based view for displaying objects.
    Attributes:
        template_name (str): Path to the template used for rendering the watchlist page.
        context_object_name (str): Name of the context variable to access the movies in the template.
    Methods:
        get_queryset(): Retrieves the list of movies in the watchlist for the current user.
    """
    template_name = 'reviewapp/watchlist.html'
    context_object_name = 'movies'

    def get_queryset(self):
        return Movie.objects.filter(watchlist__user=self.request.user)