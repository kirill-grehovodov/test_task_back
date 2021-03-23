import requests
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView

from src.followers.models import FollowerCountry
from src.webapp.models import Post, Tag, get_countries


class IndexView(ListView):
    template_name = 'index.html'
    model = Post
    context_object_name = 'posts'
    paginate_by = 2

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_list_countries_codes(self, code):
        return code[0]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        countries = Post.objects.all().values_list('country_code')
        countries_codes = list(set(map(self.get_list_countries_codes, countries)))

        context['countries'] = get_countries(
            "https://restcountries.eu/rest/v2/alpha?codes=" + ";".join(countries_codes))

        # if self.request.user.groups.filter(name__in=['Team Lead', 'Project Manager']):
        #     context['user_list_perm'] = True
        # context['form'] = self.form

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:

            users_subscribe_posts = Q(author__subscribers__user__pk=user.pk)
            users_subscribe_tags = Q(tags__tag_users__user__pk=user.pk)
            countries_codes = FollowerCountry.objects.filter(user_id=user.pk).values_list("country")

            users_subscribe_countries = Q(country_code__in=countries_codes)
            my_posts = Q(author__id=user.pk)
            queryset = queryset.filter(
                users_subscribe_tags | users_subscribe_posts | users_subscribe_countries).exclude(
                my_posts).distinct().order_by(
                "-created_at")
            print(queryset)
        else:
            queryset = queryset.order_by('-created_at')[:3]
        return queryset


class CountryView(ListView):
    template_name = 'country.html'
    model = Post
    context_object_name = 'posts'
    paginate_by = 2

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['country'] = requests.get(
            "https://restcountries.eu/rest/v2/alpha/" + self.kwargs.get("code")).json()

        # if self.request.user.groups.filter(name__in=['Team Lead', 'Project Manager']):
        #     context['user_list_perm'] = True
        # context['form'] = self.form

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        print(self.kwargs.get('code'))
        queryset = queryset.filter(country_code=self.kwargs.get('code'))
        return queryset
