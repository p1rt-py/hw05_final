import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post

from ..forms import PostForm

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.form = PostForm()

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создаёт запись"""
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст формы',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=self.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_form_update(self):
        """Проверка редактирования поста через форму на странице"""
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small_1.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.id,
            'text': 'Обновленный текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data, follow=True)
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=(self.post.id,)))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=form_data['group'],
            author=self.user,
            image='posts/small_1.gif'
        ).exists())

    def test_add_comment_authorizet(self):
        """Валидная форма создает CommentForm."""
        comment_count = Comment.objects.count()
        form_data = {
            'author': self.user,
            'text': 'комментарий',
            'post': self.post,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data=form_data, follow=True)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=(self.post.id,)
        ))
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text']
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        comment = Comment.objects.first()
        comment_text = comment.text
        self.assertEqual(comment_text, form_data['text'])

    def test_add_comment_client(self):
        comment_count = Comment.objects.count()
        response = self.client.post(
            reverse(
                'posts:add_comment', args=(self.post.id,)
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/')
        self.assertEqual(Comment.objects.count(), comment_count)
