from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView

from src.webapp.models import Post


class IndexView(ListView):
    template_name = 'index.html'
    model = Post
    context_object_name = 'posts'
    paginate_by = 2

    def get(self, request, *args, **kwargs):
        # self.form = self.get_search_form()
        # self.search_value = self.get_search_value()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        # if self.request.user.groups.filter(name__in=['Team Lead', 'Project Manager']):
        #     context['user_list_perm'] = True
        # context['form'] = self.form
        # if self.search_value:
        #     context['query'] = urlencode({'search': self.search_value})
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        # if self.search_value:
        #     query = Q(name__icontains=self.search_value) | Q(description__icontains=self.search_value)
        #     queryset = queryset.filter(query)
        return queryset

    # def get_search_form(self):
    #     return SearchForm(self.request.GET)
    #
    # def get_search_value(self):
    #     if self.form.is_valid():
    #         return self.form.cleaned_data['search']
    #     return None