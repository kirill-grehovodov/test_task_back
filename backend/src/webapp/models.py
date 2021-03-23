from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
import requests


def get_countries(url):
    countries = requests.get(url)

    def get_choice(country):
        return country['alpha2Code'], country['name']

    countries_lookup = list(map(get_choice, countries.json()))
    return countries_lookup


class Post(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False, verbose_name='Заголовок',
                             validators=[MinLengthValidator(10)])
    text = models.TextField(max_length=3000, null=False, blank=False, verbose_name='Текст',
                            validators=[MinLengthValidator(3)])
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_DEFAULT, default=1,
                               related_name='posts', verbose_name='Автор')
    tags = models.ManyToManyField('webapp.Tag', related_name='tags', blank=True, verbose_name='Теги')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время изменения')
    rating = models.IntegerField(verbose_name="Счётчик лайков", default=0)
    is_locked = models.BooleanField(default=False)
    country_code = models.CharField(max_length=200, choices=get_countries('https://restcountries.eu/rest/v2/all'), verbose_name='Страна')

    def __str__(self):
        return "{}. {}".format(self.pk, self.title)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    post = models.ForeignKey('webapp.Post', related_name='comments',
                             on_delete=models.CASCADE, verbose_name='Пост')
    text = models.TextField(max_length=400, verbose_name='Комментарий')
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_DEFAULT, default=1,
                               related_name='comments', verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время изменения')

    def __str__(self):
        return self.text[:20]

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Tag(models.Model):
    name = models.CharField(max_length=31, verbose_name='Тег')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class PostRate(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             related_name='post_likes', verbose_name='Пользователь')
    post = models.ForeignKey('webapp.Post', on_delete=models.CASCADE,
                             related_name='likes', verbose_name='Пост')

    def __str__(self):
        return f'{self.user.username} - {self.article.title}'

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'


class PostImage(models.Model):
    post = models.ForeignKey('webapp.Post', on_delete=models.CASCADE,
                             related_name='images', verbose_name='Пост')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        verbose_name = 'Фото'
        verbose_name_plural = 'Фото'