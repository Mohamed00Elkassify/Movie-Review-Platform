from django.shortcuts import render
from django.views.generic import FormView
from .forms import RegisterForm
from django.urls import reverse_lazy
# Create your views here.

class RegisterView(FormView):
    template_name = 'registration/signup.html'
    form_class = RegisterForm
    succes_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)