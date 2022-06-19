from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from posts.models import Group, Post, Comment

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом
        Созданный пост появился на стартовой странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        post = response.context['page_obj'][0]
        index_text_0 = post.text
        index_author_0 = post.author.username
        index_group_slug_0 = post.group.slug
        self.assertEqual(index_text_0, self.post.text)
        self.assertEqual(index_author_0, self.user.username)
        self.assertEqual(index_group_slug_0, self.group.slug)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом
        Созданный пост появился на странице группы"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertIn('page_obj', response.context)
        post = response.context['page_obj'][0]
        index_text_0 = post.text
        index_author_0 = post.author.username
        index_group_slug_0 = post.group.slug
        self.assertEqual(index_text_0, self.post.text)
        self.assertEqual(index_author_0, self.user.username)
        self.assertEqual(index_group_slug_0, self.group.slug)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом
        Созданный пост появился на странице профиля автора"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertIn('page_obj', response.context)
        post = response.context['page_obj'][0]
        index_text_0 = post.text
        index_author_0 = post.author.username
        index_group_slug_0 = post.group.slug
        self.assertEqual(index_text_0, self.post.text)
        self.assertEqual(index_author_0, self.user.username)
        self.assertEqual(index_group_slug_0, self.group.slug)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом
         информация поста появляется на отдельной странице"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context.get('post').text, self.post.text)

    def test_follow_index_show_cont(self):
        """Шаблон follow сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:follow_index'))
        post_follow_count = len(response.context['page_obj'])
        new_author = User.objects.create_user(username='new')
        Post.objects.create(
            author=new_author,
            text='Новый тестовый пост',
        )
        self.authorized_client.get(reverse('posts:follow',
                                           new_author.username))
        response = self.authorized_client.get(reverse(
            'posts:follow_index'))
        self.assertEqual(
            len(response.context['page_obj']),
            post_follow_count + 1)

    def test_add_comment_guest(self):
        """Пользователь не может комментировать неавторизованным"""
        form_data = {'next': 'Текст комментария'}
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertNotEqual(response.context_decode(), form_data['text'])

    def test_add_comment(self):
        """Комментировать посты может только авторизованный"""
        comments_count = Comment.objects.count()
        form_data = {'text': 'Текст комментария'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertRedirects(response, reverse('posts:post_detail'),
                             kwargs={'post_id': self.post.id})
        self.assert_True(Comment.objects.filter(
            text=form_data['text']).exists()
                         )

    def test_add_comment_guest2(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария'
            'author: self.guest_client'
        }
        self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)

    def test_index_page_cache_work_correct(self):
        """Кэширование постов на главной странице"""
        post = Post.objects.creare(
            text='Test cache', author={PostViewsTests.user}
        )
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        post.delete()
        response2 = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertIn('page_obj', response.content, 'Не найден'),
        self.assertIn('page_obj', response2.content, 'Не найден')
        self.assertEqual(response.content['page_obj'][0],
                         response2.content['page_obj'][0]
                         )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        Post.objects.bulk_create(
            [Post(text='text', author=cls.user) for i in range(13)]
        )

    def test_paginator_first_page_contains_10_posts(self):
        """Колличество постов на первой странице равно 10"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_paginator_second_page_contains_3_posts(self):
        response = self.guest_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
