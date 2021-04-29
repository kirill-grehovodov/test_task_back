from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from api.constans import PAGINATION_PAGE_COUNT
from api.serializers import ListPostSerializer
from src.followers.models import FollowerCountry
from src.webapp.models import Post, Comment


class SignInViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test',
                                                         password='12test12',
                                                         email='test@example.com')

    def tearDown(self):
        self.user.delete()

    def test_correct(self):
        response = self.client.post('/auth/token/login/', {'username': 'test', 'password': '12test12'})

        self.assertTrue(response.data['auth_token'])

    def test_wrong_username(self):
        response = self.client.post('/auth/token/login/', {'username': 'wrong', 'password': '12test12'})
        self.assertFalse(response.data.get('auth_token'))

    def test_wrong_pssword(self):
        response = self.client.post('/auth/token/login/', {'username': 'test', 'password': 'wrong'})
        self.assertFalse(response.data.get('auth_token'))


class AllPostsViewTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test',
                                                         password='12test12',
                                                         email='test@example.com')
        response = self.client.post('/auth/token/login/', {'username': 'test', 'password': '12test12'})
        self.token = response.data.get('auth_token')

    def tearDown(self):
        self.user.delete()

    def test_no_posts(self):
        response = self.client.get('/api/posts/')
        self.assertEqual(response.data, {'links': {'next': None, 'previous': None}, 'count': 0, 'results': []})

    def test_one_post(self):
        self.post1 = Post.objects.create(author=self.user,
                                         title='test',
                                         text='description',
                                         country_code='RU', )
        response = self.client.get('/api/posts/')
        # result = ListPostSerializer(response.data.get('results'), many=True)
        # print(result.data)
        self.assertEqual(response.data,
                         {'links': {'next': None, 'previous': None}, 'count': 1, 'results': [OrderedDict(
                             [('id', 1), ('created_at', self.post1.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f") + 'Z'),
                              ('author', OrderedDict(
                                  [('id', 1), ('username', 'test')])), ('title', 'test'),
                              ('country_code', {'value': 'RU', 'display': 'Russian Federation'})])]})
        self.post1.delete()

    def test_pagination(self):
        PAGINATION_PAGE = 12
        user2 = get_user_model().objects.create_user(username='test2',
                                                     password='12test12',
                                                     email='test@example.com')
        for _ in range(PAGINATION_PAGE):
            Post.objects.create(author=user2,
                                title='test',
                                text='description',
                                country_code='RU', )
        FollowerCountry.objects.create(user=self.user, country="RU")
        FollowerCountry.objects.create(user=self.user, country="GE")
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('links' in response.data)
        self.assertTrue(len(response.data['results']) == PAGINATION_PAGE_COUNT)
        self.client.credentials(HTTP_AUTHORIZATION='Token {0}'.format(self.token))
        response = self.client.get('/api/posts/?page=2')
        self.assertTrue(len(response.data['results']) == PAGINATION_PAGE - PAGINATION_PAGE_COUNT)
        response = self.client.get('/api/country/RU')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('links' in response.data)
        self.assertTrue('country' in response.data)
        self.assertTrue(len(response.data['results']) == PAGINATION_PAGE_COUNT)
        Post.objects.all().delete()
        user2.delete()


class CommentCreateViewTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test',
                                                         password='12test12',
                                                         email='test@example.com')
        response = self.client.post('/auth/token/login/', {'username': 'test', 'password': '12test12'})
        self.token = response.data.get('auth_token')
        self.post = Post.objects.create(author=self.user,
                                        title='test',
                                        text='description',
                                        country_code='RU', )
        self.client.credentials(HTTP_AUTHORIZATION='Token {0}'.format(self.token))

    def tearDown(self):
        self.user.delete()
        self.post.delete()

    def test_comment_create(self):
        response = self.client.post('/api/1/comment/create/', {"text": "крутой пост"})
        self.assertEqual(response.status_code, 201)
        comment = Comment.objects.first()
        self.assertEqual(comment.text, "крутой пост")
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)

    def test_comment_bad_request(self):
        response = self.client.post('/api/2/comment/create/', {"text": "крутой пост"})
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/api/1/comment/create/')
        self.assertEqual(response.status_code, 400)