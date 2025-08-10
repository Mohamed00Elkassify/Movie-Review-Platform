from django.shortcuts import render
from django.views.generic import FormView, ListView, DetailView
from .forms import RegisterForm, RatingForm
from django.urls import reverse_lazy
from .models import Movie, Rating, Genre, Watchlist
from django.db.models import Avg, Count
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
            
        
