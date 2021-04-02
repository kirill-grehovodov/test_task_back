from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
from rest_framework import generics, permissions, views, response, mixins
from rest_framework.decorators import action, api_view

from api.serializers import ListPostSerializer, ListCommentByPostSerializer, CreateCommentSerializer, \
    ListPostsUserSerializer, CreatePostSerializer
from src.followers.models import FollowerUser, FollowerTag, FollowerCountry
from src.webapp.models import Tag, Post, Comment, PostRate


class UserView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListPostsUserSerializer
    queryset = User.objects.all()


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
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)

        return Response(status=status.HTTP_201_CREATED)


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

    def get_queryset(self):
        return Post.objects.all()


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

