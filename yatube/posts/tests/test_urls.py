from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            id='13'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='slug',
            description='Тестовое описание'
        )

    def test_index_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_task_group_url_exists_at_desired_location(self):
        """Страница /group/slug/ доступна любому пользователю."""
        response = self.guest_client.get('/group/slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_task_profile_url_exists_at_desired_location(self):
        """Страница /profile/auth/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/auth/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_task_post_detail_url_exists_at_desired_location(self):
        """Страница /posts/13/ доступна любому пользователю."""
        response = self.guest_client.get('/posts/13/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /posts/<int:post_id>/edit/ доступна авторизованному
        пользователю. """
        response = self.authorized_client.get('/posts/13/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """Соответствующие шаблон для общедоступных страниц."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/slug/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': '/posts/13/'
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_return_404(self):
        """Страница unexisting вернет 404."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_create_for_authorized(self):
        """Страница по адресу /create/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_anonymous(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_posts_edit_url_uses_correct_template(self):
        """Страница /added/ использует шаблон deals/added.html."""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_urls_authorized_correct_template(self):
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/follow.html')
