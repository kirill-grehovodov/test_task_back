from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status, pagination
from rest_framework import generics, permissions, views, response
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from api.constans import PAGINATION_PAGE_COUNT
from api.permissions import FixPermission
from api.serializers import ListPostSerializer, ListCommentByPostSerializer, CreateCommentSerializer, \
    ListPostsUserSerializer, CreatePostSerializer, PostSerializer
from api.service import PaginationPosts
from src.followers.models import FollowerUser, FollowerTag, FollowerCountry
from src.webapp.models import Tag, Post, Comment, PostRate
import requests


class CountryView(APIView):
    permission_classes = [FixPermission]

    def get(self, request, *args, **kwargs):
        country = requests.get("https://restcountries.eu/rest/v2/alpha/" + self.kwargs.get("code")).json()
        posts = Post.objects.filter(country_code=self.kwargs.get('code'))
        paginator = pagination.PageNumberPagination()
        page_posts = paginator.paginate_queryset(posts, request)
        pagination_json = {
            'links': {
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link()
            },
            'count': paginator.page.paginator.count,
        }
        serializer = PostSerializer(page_posts, many=True)
        response_result = {'country': country, 'links': pagination_json, 'results': serializer.data}
        return Response(response_result)


class UserView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListPostsUserSerializer
    queryset = User.objects.all()
    # pagination_class = PaginationPosts


class CreateCommentView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()
    serializer_class = CreateCommentSerializer

    def post(self, request, *args, **kwargs):
        try:
            self.post = Post.objects.get(pk=self.kwargs.get('pk'))
            return self.create(request, *args, **kwargs)
        except Post.DoesNotExist:
            return response.Response(status=404)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.post)


class CreatePostView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = CreatePostSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = self.perform_create(serializer)
            # headers = self.get_success_headers(serializer.data)
            return Response(data=data, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

class PostView(generics.RetrieveAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListCommentByPostSerializer
    queryset = Post.objects.all()


@api_view(['POST'])
def like(request, pk=None):
    """Лайкает `obj`.
    """
    print("like")
    try:
        post_rate = PostRate.objects.get(post=pk, user=request.user)
        post_rate.rate = 1
        post_rate.save()
    except PostRate.DoesNotExist:
        PostRate.objects.create(post=pk, user=request.user, rate=1)
    # services.add_like(obj, request.user)
    return Response()


@api_view(['POST'])
def dislike(request, pk=None):
    """Удаляет лайк с `obj`.
    """
    try:
        post_rate = PostRate.objects.get(post=pk, user=request.user)
        post_rate.rate = -1
        post_rate.save()
    except PostRate.DoesNotExist:
        PostRate.objects.create(post=pk, user=request.user, rate=-1)
    # services.remove_like(obj, request.user)
    return Response()


class PostListView(generics.ListAPIView):
    serializer_class = ListPostSerializer
    pagination_class = PaginationPosts

    def get_queryset(self):
        queryset = Post.objects.all()
        user = self.request.user
        if user.is_authenticated:
            users_subscribe_posts = Q(author__subscribers__user__pk=user.pk)
            users_subscribe_tags = Q(tags__tag_users__user__pk=user.pk)
            countries_codes = FollowerCountry.objects.filter(user_id=user.pk).values_list("country")
            users_subscribe_countries = Q(country_code__in=countries_codes)
            my_posts = Q(author__id=user.pk)
            queryset = queryset.filter(
                users_subscribe_tags | users_subscribe_posts | users_subscribe_countries).exclude(
                my_posts).order_by("-created_at").distinct()
        else:
            queryset = queryset.order_by("-created_at")[:PAGINATION_PAGE_COUNT]
        return queryset


class FollowerView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            # pk = request.data.get('pk')
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return response.Response(status=404)
        FollowerUser.objects.create(subscriber=user, user=request.user)
        return response.Response(status=201)

    def delete(self, request, pk):
        try:
            sub = FollowerUser.objects.get(subscriber_id=pk, user=request.user)
        except FollowerUser.DoesNotExist:
            return response.Response(status=404)
        sub.delete()
        return response.Response(status=204)


class UserTagView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            tag = Tag.objects.get(id=pk)
        except Tag.DoesNotExist:
            print("error")
            return response.Response(status=404)
        FollowerTag.objects.create(user=request.user, tag=tag)
        return response.Response(status=201)

    def delete(self, request, pk):
        try:
            sub = FollowerTag.objects.get(user=request.user, tag_id=pk)
        except FollowerTag.DoesNotExist:
            return response.Response(status=404)
        sub.delete()
        return response.Response(status=204)


class UserCountryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, code):
        # print(request.data.get('code'))
        FollowerCountry.objects.create(user=request.user, country=code)
        return response.Response(status=201)

    def delete(self, request, code):
        try:
            sub = FollowerCountry.objects.get(user=request.user, country=code)
        except FollowerCountry.DoesNotExist:
            return response.Response(status=404)
        sub.delete()
        return response.Response(status=204)

