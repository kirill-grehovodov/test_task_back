from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.test import TestCase

from api.serializers import ListPostSerializer
from src.webapp.models import Post


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


class AllPostsViewTest(TestCase):
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
        print(response.data)
        result = ListPostSerializer(response.data.get('results'), many=True)
        print(result.data)
        self.assertEqual(response.data,
                         {'links': {'next': None, 'previous': None}, 'count': 1, 'results': [OrderedDict(
                             [('id', 1), ('created_at', self.post1.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")+'Z'),
                              ('author', OrderedDict(
                                  [('id', 1), ('username', 'test')])), ('title', 'test'),
                              ('country_code', {'value': 'RU', 'display': 'Russian Federation'})])]})
        self.post1.delete()