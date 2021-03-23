from django.contrib.auth import get_user_model
from django.db import models

from src.webapp.models import get_countries


class FollowerUser(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='subscribed_to', verbose_name='Подписчик'
    )
    subscriber = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='subscribers', verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')


class FollowerTag(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='user_tags', verbose_name='Пользователь'
    )
    tag = models.ForeignKey("webapp.Tag", on_delete=models.CASCADE, related_name='tag_users', verbose_name='Тег')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')


class FollowerCountry(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='user_countries', verbose_name='Пользователь'
    )
    country = models.CharField(max_length=200, choices=get_countries('https://restcountries.eu/rest/v2/all'),
                               verbose_name='Страна')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
