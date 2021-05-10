from django.contrib.auth import get_user_model
from django.test import TestCase

# Create your tests here.
from src.webapp.models import Post, PostRate


# class PostTest(TestCase):
#     def setUp(self):
#         self.user = get_user_model().objects.create_user(username='test', password='12test12', email='test@example.com')
#         self.user.save()
#         self.post = Post.objects.create(author=self.user,
#                                         title='test',
#                                         text='description',
#                                         country_code='RU')
#         self.post.save()
#         self.like1 = PostRate.objects.create(
#             user=self.user,
#             post=self.post,
#             rate=1
#         )
#         self.like2 = PostRate.objects.create(
#             user=self.user,
#             post=self.post,
#             rate=1
#         )
#
#     def tearDown(self):
#         self.post.delete()
#         self.user.delete()
#
#     def test_read_post(self):
#         self.assertEqual(self.post.author, self.user)
#         self.assertEqual(self.post.text, 'description')
#
#     def test_update_task_description(self):
#         self.post.text = 'new description'
#         self.post.save()
#         self.assertEqual(self.post.text, 'new description')
#
#     def test_total_likes(self):
#         self.assertEqual(self.post.total_likes, (self.like1.rate+self.like2.rate))
