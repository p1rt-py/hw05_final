from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, Comment

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'title': 'Заголовой из формы',
            'text': 'Текст из формы',
            'slug': 'test-slug1',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': PostCreateFormTests.user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostCreateFormTests.group,
                author=PostCreateFormTests.user,
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_authorized_client(self):
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='small/gif'
        )
        form_data = {
            'text': 'Тестовый пост 2',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
         )
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Тестовый текст 2',
            group=self.group.id,
            image='posts/small.gif'
        ).exists()
        )

    def test_authorized_edit_post(self):
        post = Post.objects.get(pk=self.group.id)
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(pk=self.group.id)
        self.assertEqual(response_edit.status_code, HTTPStatus.OK)

    def test_unauthorized_try_comment(self):
        """Проверка создания анонимного комментирия"""
        form_data = {
            'text': 'text',
        }
        reverse_name = reverse('posts:add_comment', args=(self.post.id,))
        response = self.client.post(
            reverse_name,
            data=form_data,
            follow=True,
        )
        login = reverse('users:login')
        add_comment = reverse('posts:add_comment', args=(self.post.id,))
        self.assertRedirects(response, f'{login}?next={add_comment}')
        self.assertEqual(Comment.objects.count(), 0)
