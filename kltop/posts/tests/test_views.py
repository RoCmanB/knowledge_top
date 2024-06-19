import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.urls import reverse
from django import forms

from ..models import Follow, Group, Post
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache


PAGINUM = settings.PAGI_NUM

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PathsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем авторизованный и не авторизованный клиен.
        Добавляем запись во временную БД.
        """
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.follow_author = User.objects.create_user(username='follow-author')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.other_user = User.objects.create_user(username='other_user')
        cls.other_authorized_client = Client()
        cls.other_authorized_client.force_login(cls.other_user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.image
        )
        cls.INDEX_REV = reverse('posts:index')
        cls.GROUP_REV = reverse('posts:group_list',
                                kwargs={'slug': f'{cls.group.slug}'})
        cls.PROFILE_REV = reverse('posts:profile',
                                  kwargs={'username': f'{cls.user.username}'})
        cls.POST_REV = reverse('posts:post_detail',
                               kwargs={'post_id': f'{cls.post.id}'})
        cls.CREATE_REV = reverse('posts:post_create')
        cls.POST_EDIT_REV = reverse('posts:post_edit',
                                    kwargs={'post_id': f'{cls.post.id}'})
        cls.COMMENT_REV = reverse('posts:add_comment',
                                  kwargs={'post_id': f'{cls.post.id}'})
        cls.PROFILE_FOLLOW_REV = reverse(
            'posts:profile_follow',
            kwargs={'username': f'{cls.follow_author.username}'}
        )
        cls.PROFILE_UNFOLLOW_REV = reverse(
            'posts:profile_unfollow',
            kwargs={'username': f'{cls.follow_author.username}'}
        )
        cls.FOLLOW_INDEX = reverse('posts:follow_index')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    # Task #1
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            self.INDEX_REV: 'posts/index.html',
            self.GROUP_REV: 'posts/group_list.html',
            self.PROFILE_REV: 'posts/profile.html',
            self.POST_REV: 'posts/post_detail.html',
            self.CREATE_REV: 'posts/create_post.html',
            self.POST_EDIT_REV: 'posts/create_post.html',
        }
        for reverse_name, url in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, url)

    # Task #2
    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.INDEX_REV)
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)
        self.assertTrue(post.image)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.GROUP_REV)
        group_title = response.context['group']
        post = response.context['page_obj'][0]
        self.assertEqual(group_title, self.group)
        self.assertTrue(post.image)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.PROFILE_REV)
        post_auth = response.context['page_obj'][0]
        posts = response.context['posts'][0]
        self.assertEqual(post_auth.author, self.user)
        self.assertEqual(posts, self.post)
        self.assertTrue(posts.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_REV)
        post = response.context['post']
        self.assertEqual(post, self.post)
        self.assertTrue(post.image)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.CREATE_REV)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_EDIT_REV)
        post = response.context['post']
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(post, self.post)

    # Task #3
    def test_post_appears_on_homepage(self):
        response = self.client.get(self.INDEX_REV)
        self.assertContains(response, self.post.text)

    def test_post_appears_on_group_page(self):
        response = self.client.get(self.GROUP_REV)
        self.assertContains(response, self.post.text)

    def test_post_appears_on_user_profile(self):
        response = self.client.get(self.PROFILE_REV)
        self.assertContains(response, self.post.text)

    def test_add_comment_only_authorized_client(self):
        """Комментарий может добавить только авторизованный
        пользователь.
        """
        initial_comments_num = self.post.comments.all().count()
        form_data = {'text': 'Какой-то комментарий номер #2'}
        self.guest_client.post(
            self.COMMENT_REV,
            data=form_data,
            follow=True
        )
        final_comments_num = self.post.comments.all().count()
        self.assertEqual(final_comments_num, initial_comments_num)

    def test_index_cache_works(self):
        """Проверка, что посты на главной странице кэшируются"""
        post_cache = Post.objects.create(
            author=self.user,
            text='Тестовый пост для проверки кеша',
        )
        response = self.authorized_client.get(self.INDEX_REV)
        post_cache.delete()
        new_response = self.authorized_client.get(self.INDEX_REV)
        self.assertEqual(response.content, new_response.content)
        cache.clear()
        last_response = self.authorized_client.get(self.INDEX_REV)
        self.assertNotEqual(response.content, last_response.content)

    def test_follow_author(self):
        """Для авторизованного пользователя возможна подписка."""
        original_follow = Follow.objects.count()
        self.authorized_client.get(self.PROFILE_FOLLOW_REV)
        actual_follow = Follow.objects.count()
        new_follow = Follow.objects.first()
        follow_date = {
            new_follow.user: self.user,
            new_follow.author: self.follow_author,
        }
        for follow_value, form_date in follow_date.items():
            with self.subTest(valfollow_valueue=follow_value):
                self.assertEqual(follow_value, form_date)
        self.assertEqual(actual_follow, original_follow + 1)

    def test_unfollow_author(self):
        """Для авторизованного пользователя возможна отписка."""
        original_follow = Follow.objects.count()
        Follow.objects.create(user=self.user,
                              author=self.follow_author)
        self.authorized_client.get(self.PROFILE_UNFOLLOW_REV)
        actual_follow = Follow.objects.count()
        self.assertEqual(actual_follow, original_follow)
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.follow_author
        ).exists())

    def test_post_in_follow_pages(self):
        """Запись автора появляется в ленте подписчиков."""
        self.authorized_client.get(self.PROFILE_FOLLOW_REV)
        new_post = Post.objects.create(
            author=self.follow_author,
            text='Тестовый пост для подписчика',
        )
        response = self.authorized_client.get(self.FOLLOW_INDEX)
        self.assertIn(new_post, response.context['page_obj'])

    def test_post_in_not_follow_pages(self):
        """Запись автора не появляется в ленте подписчиков."""
        new_post = Post.objects.create(
            author=self.follow_author,
            text='Тестовый пост для подписчиков',
        )
        response = self.other_authorized_client.get(self.FOLLOW_INDEX)
        self.assertNotIn(new_post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
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
        posts = [
            Post(
                author=cls.user,
                text=f'Тестовый текст # {i}',
                group=cls.group)
            for i in range(123)
        ]
        Post.objects.bulk_create(posts)
        cls.paginator = Paginator(Post.objects.all(), PAGINUM)
        cls.last_page = cls.paginator.count % PAGINUM
        cls.INDEX_REV = reverse('posts:index')
        cls.GROUP_REV = reverse('posts:group_list',
                                kwargs={'slug': f'{cls.group.slug}'})
        cls.PROFILE_REV = reverse('posts:profile',
                                  kwargs={'username': f'{cls.user.username}'})

    def test_paginator(self):
        """Проверка работы паджинатора"""
        page_obj_num = {
            self.INDEX_REV: PAGINUM,
            self.INDEX_REV + f'?page={self.paginator.num_pages}':
            self.last_page,
            self.GROUP_REV: PAGINUM,
            self.GROUP_REV + f'?page={self.paginator.num_pages}':
            self.last_page,
            self.PROFILE_REV: PAGINUM,
            self.PROFILE_REV + f'?page={self.paginator.num_pages}':
            self.last_page,
        }
        for reverse_name, page_num in page_obj_num.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), page_num)
