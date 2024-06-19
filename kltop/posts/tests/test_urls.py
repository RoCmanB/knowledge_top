from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

from ..models import Group, Post
from django.urls import reverse


User = get_user_model()


class UrlsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем авторизованный и не авторизованный клиен.
        Добавляем запись во временную БД.
        """
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.COMMENT_REV = reverse('posts:add_comment',
                                  kwargs={'post_id': f'{cls.post.id}'})
        cls.INDEX_URL = '/'
        cls.GROUP_URL = f'/group/{cls.group.slug}/'
        cls.PROFILE_URL = f'/profile/{cls.user.username}/'
        cls.POST_URL = f'/posts/{cls.post.id}/'
        cls.POST_EDIR_URL = f'/posts/{cls.post.id}/edit/'
        cls.CREATE_URL = '/create/'
        cls.UNKNOWN_URL = '/unexisting_page/'
        cls.FOLLOW_URL = '/follow/'
        cls.COMMENT_URL = f'/posts/{cls.post.id}/comment/'
        cls.PROFILE_FOLLOW_URL = f'/profile/{cls.user.username}/follow/'
        cls.PROFILE_UNFOLLOW_URL = f'/profile/{cls.user.username}/unfollow/'

    def test_html_templates(self):
        """Тест проверяет страницу и её шаблон."""
        templates_url_names = {
            self.INDEX_URL: 'posts/index.html',
            self.GROUP_URL: 'posts/group_list.html',
            self.PROFILE_URL: 'posts/profile.html',
            self.POST_URL: 'posts/post_detail.html',
            self.POST_EDIR_URL: 'posts/create_post.html',
            self.CREATE_URL: 'posts/create_post.html',
            self.UNKNOWN_URL: 'core/404.html',
            self.FOLLOW_URL: 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_status_code_for_guest(self):
        """Тест проверяет ожидаемый статус старницы всех
        адресов сайта для неавторизованного пользователя.
        """
        pages_code_status = {
            self.INDEX_URL: HTTPStatus.OK,
            self.GROUP_URL: HTTPStatus.OK,
            self.PROFILE_URL: HTTPStatus.OK,
            self.POST_URL: HTTPStatus.OK,
            self.POST_EDIR_URL: HTTPStatus.FOUND,
            self.CREATE_URL: HTTPStatus.FOUND,
            self.UNKNOWN_URL: HTTPStatus.NOT_FOUND,
            self.FOLLOW_URL: HTTPStatus.FOUND,
            self.COMMENT_URL: HTTPStatus.FOUND,
            self.PROFILE_FOLLOW_URL: HTTPStatus.FOUND,
            self.PROFILE_UNFOLLOW_URL: HTTPStatus.FOUND,
        }
        for address, status in pages_code_status.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_status_code_for_auth(self):
        """Тест проверяет ожидаемый статус старницы всех
        адресов сайта для авторизованного пользователя.
        """
        pages_code_status = {
            self.INDEX_URL: HTTPStatus.OK,
            self.GROUP_URL: HTTPStatus.OK,
            self.PROFILE_URL: HTTPStatus.OK,
            self.POST_URL: HTTPStatus.OK,
            self.POST_EDIR_URL: HTTPStatus.OK,
            self.CREATE_URL: HTTPStatus.OK,
            self.UNKNOWN_URL: HTTPStatus.NOT_FOUND,
            self.FOLLOW_URL: HTTPStatus.OK,
            self.COMMENT_URL: HTTPStatus.FOUND,
            self.PROFILE_FOLLOW_URL: HTTPStatus.FOUND,
            self.PROFILE_UNFOLLOW_URL: HTTPStatus.FOUND,
        }
        for address, status in pages_code_status.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status)
