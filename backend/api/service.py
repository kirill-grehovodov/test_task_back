from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from src.webapp.models import Post


class PaginationPosts(PageNumberPagination):
    page_size = 2
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })

    # def paginate_queryset(self, queryset, request, view=None):
    #     print('frferec')
    #     print(request.GET.get('pk'), 'pk')
    #     queryset = Post.objects.filter(author__id=request.GET.get('pk'))
    #     return super().paginate_queryset(queryset, request, view=None)