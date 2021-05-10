import six
from django.contrib.auth.models import User
from rest_framework import serializers, pagination
from rest_framework.fields import ChoiceField

from src.webapp.models import PostImage, Post, Comment, Tag, get_countries


# class ChoiceField(serializers.ChoiceField):
#
#     def to_representation(self, obj):
#         return self._choices[obj]

class StringListField(serializers.ListField):
    child = serializers.CharField()


class ChoiceDisplayField(ChoiceField):
    def __init__(self, *args, **kwargs):
        super(ChoiceDisplayField, self).__init__(*args, **kwargs)
        self.choice_strings_to_display = {
            six.text_type(key): value for key, value in self.choices.items()
        }

    def to_representation(self, value):
        if value is None:
            return value
        return {
            'value': self.choice_strings_to_values.get(six.text_type(value), value),
            'display': self.choice_strings_to_display.get(six.text_type(value), value),
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class ListPostSerializer(serializers.ModelSerializer):
    serializer_choice_field = ChoiceDisplayField
    # author_name = serializers.ReadOnlyField(source='author.username')
    author = UserSerializer()

    class Meta:
        model = Post
        fields = ("id", "created_at", "author", "title", "country_code")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class PostSerializer(serializers.ModelSerializer):
    serializer_choice_field = ChoiceDisplayField
    author = UserSerializer()
    tags = TagSerializer(many=True, read_only=True)
    # country_code = ChoiceField(choices=get_countries('https://restcountries.eu/rest/v2/all'))

    class Meta:
        model = Post
        fields = ("id", "created_at", "author", "title", "country_code", "tags", "text")


class CreateCommentSerializer(serializers.ModelSerializer):
    text = serializers.CharField(required=True, min_length=2)

    class Meta:
        model = Comment
        fields = ("text", "author")


class CommentSerializer(serializers.ModelSerializer):

    author = UserSerializer()

    class Meta:
        model = Comment
        fields = ("text", "author", "created_at", "id")


class ListCommentByPostSerializer(serializers.ModelSerializer):
    serializer_choice_field = ChoiceDisplayField
    """ Список комментариев
    """
    author = UserSerializer()
    comments = CommentSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ("id", "author", "text", "created_at", "country_code", "comments", "tags")


class ListPostsUserSerializer(serializers.ModelSerializer):

    posts = serializers.SerializerMethodField('event_posts')
    pagination = serializers.SerializerMethodField('get_paginated')

    def event_posts(self, obj):
        posts = Post.objects.filter(author=obj)
        paginator = pagination.PageNumberPagination()
        page = paginator.paginate_queryset(posts, self.context['request'])
        self.paginator = paginator
        serializer = PostSerializer(page, many=True, context={'request': self.context['request']})
        return serializer.data

    def get_paginated(self, obj):
        return ({
            'links': {
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link()
            },
            'count': self.paginator.page.paginator.count,
        })

    class Meta:
        model = User
        fields = ("id", "username",  "email", "posts", "pagination")


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('image',)


class CreatePostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(source='image_set', many=True, read_only=True)
    tags = StringListField(required=False)

    class Meta:
        model = Post
        fields = ('title', 'images', 'text', 'tags', 'country_code',)

    def create(self, validated_data):
        images_data = self.context.get('view').request.FILES
        if images_data:
            if len(images_data.getlist('images')) > 10:
                raise serializers.ValidationError(detail="Картинок может быть максимум 10")
            for img in images_data.getlist('images'):
                if img.name.split('.')[1] not in ['jpg', 'jpeg', 'png']:
                    raise serializers.ValidationError("Неверный формат картинки")
                if img.size > 5242880:
                    raise serializers.ValidationError("Размер картинки превышает 5mb")

        tags = validated_data.get('tags')
        post = Post.objects.create(title=validated_data.get('title'),
                                   text=validated_data.get('text'),
                                   country_code=validated_data.get('country_code'),
                                   author=validated_data.get('author'))
        if tags:
            for tag in tags:
                try:
                    Tag.objects.get(name=tag)
                except Tag.DoesNotExist:
                    Tag.objects.create(name=tag)
            post_tags = Tag.objects.filter(name__in=tags)
            post.tags.set(list(post_tags))
        if images_data:
            for image_data in images_data.values():
                PostImage.objects.create(post=post, image=image_data)
        return {"id": post.id}
