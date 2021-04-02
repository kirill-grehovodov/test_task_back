from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import Sum

from src.webapp.models import Post, Tag, PostRate


def general_information(request):
    posts = Post.objects.order_by('-created_at')[:3]
    tags = Tag.objects.all()
    users_id = PostRate.objects.values('user').annotate(total_rating=Sum('rate')).order_by('-total_rating')[:5]
    users = User.objects.filter(pk__in=map(lambda u: u['user'], users_id))
    # users = User.objects.annotate(total_rating=Sum('posts__total_likes')).order_by('-total_rating')[:5]
    return {'main_posts': posts, 'main_tags': tags, 'main_users': users}