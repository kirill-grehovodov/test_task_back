import uuid
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from api.constans import PAGINATION_PAGE_COUNT

from src.followers.models import FollowerCountry
from src.webapp.models import Post, Comment, Tag, PostImage

from io import BytesIO
from PIL import Image
from django.core.files.base import File


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
        self.assertEqual({'links': {'next': None, 'previous': None}, 'count': 0, 'results': []}, response.data)

    def test_one_post(self):
        self.post1 = Post.objects.create(author=self.user,
                                         title='testtesttest',
                                         text='description',
                                         country_code='RU', )
        response = self.client.get('/api/posts/')
        # result = ListPostSerializer(response.data.get('results'), many=True)
        # print(result.data)
        self.assertDictEqual(
                             {"links": {
                                 "next": None,
                                 "previous": None
                             },
                                 "count": 1,
                                 "results": [
                                     {
                                         "id": 1,
                                         "created_at": self.post1.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f") + 'Z',
                                         "author": {
                                             "id": 1,
                                             "username": "test"
                                         },
                                         "title": "testtesttest",
                                         "country_code": {
                                             "value": "RU",
                                             "display": "Russian Federation"
                                         }
                                     }
                                 ]
                             }, response.data
                             )
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
        self.assertEqual(200, response.status_code)
        self.assertTrue('links' in response.data)
        self.assertTrue(len(response.data['results']) == PAGINATION_PAGE_COUNT)
        self.client.credentials(HTTP_AUTHORIZATION='Token {0}'.format(self.token))
        response = self.client.get('/api/posts/?page=2')
        self.assertTrue(len(response.data['results']) == PAGINATION_PAGE - PAGINATION_PAGE_COUNT)
        response = self.client.get('/api/country/RU')
        self.assertEqual(200, response.status_code)
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
        self.assertEqual(201, response.status_code)
        comment = Comment.objects.first()
        self.assertEqual("крутой пост", comment.text)
        self.assertEqual(self.post, comment.post)
        self.assertEqual(self.user, comment.author)

    def test_comment_bad_request(self):
        response = self.client.post('/api/2/comment/create/', {"text": "крутой пост"})
        self.assertEqual(404, response.status_code)
        response = self.client.post('/api/1/comment/create/')
        self.assertEqual(400, response.status_code)


class PostCreateViewTest(APITestCase):
    @staticmethod
    def get_image_file(name, ext='png', size=(50, 50), color=(256, 0, 0), length=5):
        file_obj = BytesIO()
        file_obj.write(b'a' * ((length ** 2)*6))
        image = Image.new("RGBA", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return File(file_obj, name=name)

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test',
                                                         password='12test12',
                                                         email='test@example.com')
        response = self.client.post('/auth/token/login/', {'username': 'test', 'password': '12test12'})
        self.token = response.data.get('auth_token')

    def tearDown(self):
        self.user.delete()

    def test_post_no_authenticated(self):
        response = self.client.post('/api/post/create/', {})
        self.assertEqual(401, response.status_code)

    def test_create_post_success(self):
        post_data = {
            "title": "testtesttest",
            "text": "test text",
            "country_code": "RU"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token {0}'.format(self.token))
        response = self.client.post('/api/post/create/', post_data)
        self.assertEqual(201, response.status_code)
        self.assertTrue('id' in response.data)
        post = Post.objects.first()
        self.assertEqual("testtesttest", post.title)
        post.delete()

    def test_title_min_length_validation(self):
        post_data = {
            "title": "test",
            "text": "test text",
            "country_code": "RU"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token {0}'.format(self.token))
        response = self.client.post('/api/post/create/', post_data)
        self.assertEqual(400, response.status_code)
        self.assertListEqual(["Убедитесь, что это значение содержит не менее 10 символов."], response.data['title'])

    def test_country_code_validation(self):
        post_data = {
            "title": "testtesttest",
            "text": "test text",
            "country_code": "RUU"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token {0}'.format(self.token))
        response = self.client.post('/api/post/create/', post_data)
        self.assertEqual(400, response.status_code)
        self.assertListEqual(['Значения RUU нет среди допустимых вариантов.'], response.data['country_code'])

    def test_tag_to_post_create(self):
        post_data = {
            "title": "testtesttest",
            "text": "test text",
            "country_code": "RU",
            'tags': ['#test', '#test1']
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token {0}'.format(self.token))
        response = self.client.post('/api/post/create/', post_data)
        self.assertEqual(201, response.status_code)
        post = Post.objects.first()
        tag = Tag.objects.first()
        tag1 = Tag.objects.last()
        self.assertEqual("#test", tag.name)
        self.assertEqual("#test1", tag1.name)
        self.assertTrue(post.tags.count() == 2)
        post.delete()
        Tag.objects.all().delete()

    def test_does_not_create_two_identical_tag_in_db(self):
        post_data = {
            "title": "testtesttest",
            "text": "test text",
            "country_code": "RU",
            'tags': ['#test']
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token {0}'.format(self.token))
        response = self.client.post('/api/post/create/', post_data)
        self.assertEqual(201, response.status_code)
        response2 = self.client.post('/api/post/create/', post_data)
        self.assertEqual(201, response2.status_code)
        self.assertTrue(Tag.objects.all().count() == 1)
        Post.objects.all().delete()
        Tag.objects.all().delete()

    def test_image_to_post(self):
        image_name = str(uuid.uuid4())+".jpg"
        image = self.get_image_file(image_name)
        post_data = {
            "title": "testtesttest",
            "text": "test text",
            "country_code": "RU",
            'images': [image]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token {0}'.format(self.token))
        response = self.client.post('/api/post/create/', post_data)
        self.assertEqual(201, response.status_code)
        post_img = PostImage.objects.first()
        self.assertEqual('/media/posts/'+image_name, post_img.image.url)
        Post.objects.all().delete()

    def test_image_to_post_format_validation(self):
        image_name = str(uuid.uuid4())+".txt"
        image = self.get_image_file(image_name)
        post_data = {
            "title": "testtesttest",
            "text": "test text",
            "country_code": "RU",
            'images': [image]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token {0}'.format(self.token))
        response = self.client.post('/api/post/create/', post_data)
        self.assertEqual(400, response.status_code)
        self.assertListEqual(['Неверный формат картинки'], response.data)

    def test_image_to_post_max_count_validation(self):
        images = []
        for _ in range(11):
            image_name = str(uuid.uuid4())+".img"
            image = self.get_image_file(image_name)
            images.append(image)
        post_data = {
            "title": "testtesttest",
            "text": "test text",
            "country_code": "RU",
            'images': images
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token {0}'.format(self.token))
        response = self.client.post('/api/post/create/', post_data)
        self.assertEqual(400, response.status_code)
        self.assertListEqual(['Картинок может быть максимум 10'], response.data)

    def test_image_to_post_length_validation(self):
        image_name = str(uuid.uuid4())+".jpg"
        image = self.get_image_file(image_name, length=1024)
        post_data = {
            "title": "testtesttest",
            "text": "test text",
            "country_code": "RU",
            'images': [image]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token {0}'.format(self.token))
        response = self.client.post('/api/post/create/', post_data)
        self.assertEqual(400, response.status_code)
        self.assertListEqual(['Размер картинки превышает 5mb'], response.data)