import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q

from django.views.generic import ListView, DetailView

from api.constans import PAGINATION_PAGE_COUNT
from src.followers.models import FollowerCountry
from src.webapp.models import Post, get_countries


def get_list_countries_codes(code):
    return code[0]


class IndexView(ListView):
    template_name = 'index.html'
    model = Post
    context_object_name = 'posts'
    paginate_by = PAGINATION_PAGE_COUNT
    ordering = ['-created_at']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        countries = Post.objects.all().values_list('country_code')
        countries_codes = list(set(map(get_list_countries_codes, countries)))
        context['countries'] = get_countries(
            "https://restcountries.eu/rest/v2/alpha?codes=" + ";".join(countries_codes))
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
                my_posts).distinct()
        else:
            queryset = queryset[:PAGINATION_PAGE_COUNT]
        return queryset


class CountryView(LoginRequiredMixin, ListView):
    template_name = 'country.html'
    model = Post
    context_object_name = 'posts'
    paginate_by = PAGINATION_PAGE_COUNT
    ordering = ['-created_at']
    login_url = 'accounts:login'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['country'] = requests.get(
            "https://restcountries.eu/rest/v2/alpha/" + self.kwargs.get("code")).json()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(country_code=self.kwargs.get('code'))
        return queryset


class PostView(LoginRequiredMixin, DetailView):
    template_name = 'post_view.html'
    model = Post
    paginate_comments_by = 2
    paginate_comments_orphans = 0
    login_url = 'accounts:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        comments, page, is_paginated = self.paginate_comments(self.object)
        context['comments'] = comments
        context['page_obj'] = page
        context['is_paginated'] = is_paginated

        return context

    def paginate_comments(self, article):
        comments = article.comments.all().order_by('-created_at')
        if comments.count() > 0:
            paginator = Paginator(comments, self.paginate_comments_by, orphans=self.paginate_comments_orphans)
            page_number = self.request.GET.get('page', 1)
            page = paginator.get_page(page_number)
            is_paginated = paginator.num_pages > 1  # page.has_other_pages()
            return page.object_list, page, is_paginated
        else:
            return comments, None, False
