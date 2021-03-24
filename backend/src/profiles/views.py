from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import CreateView, ListView

from src.profiles.forms import MyUserCreationForm
from src.webapp.models import Post


class RegisterView(CreateView):
    model = User
    template_name = 'user_create.html'
    form_class = MyUserCreationForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('index')


class UserView(LoginRequiredMixin, ListView):
    template_name = 'user_view.html'
    model = Post
    context_object_name = 'posts'
    paginate_by = 5
    ordering = ['-created_at']
    login_url = 'accounts:login'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['user'] = User.objects.get(pk=self.kwargs.get("pk"))
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author__pk=self.kwargs.get('pk'))
