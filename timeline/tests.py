from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Comment


class TimelineTests(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='alice', password='password123')
        self.user2 = User.objects.create_user(username='bob', password='password456')

        # Create initial post
        self.post = Post.objects.create(author=self.user1, text="Hello world!")

        # Authenticated client
        self.client = Client()
        self.client.login(username='alice', password='password123')

    # --- Post Creation ---
    def test_create_post_authenticated(self):
        response = self.client.post(reverse('timeline:create'), {
            'text': 'New post from Alice'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(text='New post from Alice').exists())

    def test_create_post_unauthenticated(self):
        c = Client()
        response = c.post(reverse('timeline:create'), {'text': 'Hacker post'})
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(text='Hacker post').exists())

    # --- Edit Post ---
    def test_edit_own_post(self):
        response = self.client.post(reverse('timeline:edit', args=[self.post.pk]), {
            'text': 'Edited text'
        })
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, 'Edited text')

    def test_edit_others_post(self):
        self.client.logout()
        self.client.login(username='bob', password='password456')
        response = self.client.post(reverse('timeline:edit', args=[self.post.pk]), {
            'text': 'Bob tries to edit Alice'
        })
        self.assertEqual(response.status_code, 403)
        self.post.refresh_from_db()
        self.assertNotEqual(self.post.text, 'Bob tries to edit Alice')

    # --- Delete Post ---
    def test_delete_own_post(self):
        response = self.client.post(reverse('timeline:delete', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_delete_others_post(self):
        self.client.logout()
        self.client.login(username='bob', password='password456')
        response = self.client.post(reverse('timeline:delete', args=[self.post.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    # --- Like / Unlike ---
    def test_like_post(self):
        response = self.client.post(reverse('timeline:like', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user1, Post.objects.get(pk=self.post.pk).likes.all())

        # Toggle again to unlike
        response = self.client.post(reverse('timeline:like', args=[self.post.pk]))
        self.assertNotIn(self.user1, Post.objects.get(pk=self.post.pk).likes.all())

    # --- Comment ---
    def test_add_comment_authenticated(self):
        response = self.client.post(reverse('timeline:add_comment', args=[self.post.pk]), {
            'text': 'Nice post!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(post=self.post, text='Nice post!').exists())

    def test_add_comment_unauthenticated(self):
        c = Client()
        response = c.post(reverse('timeline:add_comment', args=[self.post.pk]), {
            'text': 'Guest comment'
        })
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(text='Guest comment').exists())

    # --- Timeline Page ---
    def test_timeline_list_accessible(self):
        response = self.client.get(reverse('timeline:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello world!")
