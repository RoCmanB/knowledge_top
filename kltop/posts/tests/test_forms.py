import shutil
import tempfile
from http import HTTPStatus

from django.test import Client, TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Comment, Group, Post
from django.conf import settings


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
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
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
            name='verysmall.gif',
            content=small_gif,
            content_type='image/gif',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.image
        )
        cls.CREATE_REV = reverse('posts:post_create')
        cls.POST_EDIT_REV = reverse('posts:post_edit',
                                    kwargs={'post_id': f'{cls.post.id}'})
        cls.LOGIN_CREATE = reverse('users:login')
        cls.COMMENT_REV = reverse('posts:add_comment',
                                  kwargs={'post_id': f'{cls.post.id}'})

    # Специально гуглил где должен стоиять метот, подвел меня гугл)
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_create(self):
        """Количество постов увеличилость
        на ожидаемое количетсво.
        """
        posts_count = Post.objects.count()
        form_data = {
            'author': self.user.username,
            'text': 'Текст из формы',
            'group': self.group.id,
            'image': self.post.image
        }
        self.authorized_client.post(
            self.CREATE_REV,
            data=form_data,
            follow=True
        )
        first_post = Post.objects.first()
        auth_post = first_post.author
        group_post = first_post.group
        text_post = first_post.text
        new_post = {
            auth_post: self.user,
            text_post: form_data['text'],
            group_post: self.group,
        }
        # Проверяем, что количество постов увеличилось.
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что данные в новом посте соответвуют, данным указанным
        # при его создании.
        for new_post_value, form_value in new_post.items():
            with self.subTest(new_post_value=new_post_value):
                self.assertEqual(new_post_value, form_value)

    def test_post_edited(self):
        """Пост отредактирован."""
        original_post = self.post
        edited_text = 'Текст из формы изменен'
        form_data = {
            'author': self.user.username,
            'text': edited_text,
            'group': self.group.id,
        }
        self.authorized_client.post(
            self.POST_EDIT_REV,
            data=form_data,
            follow=True
        )
        postedit = Post.objects.get(id=self.post.id)
        edit_post = {
            postedit.author: self.user,
            postedit.text: edited_text,
            postedit.group: self.group,
        }
        self.assertNotEqual(postedit.text, original_post.text)
        for new_post_value, form_value in edit_post.items():
            with self.subTest(new_post_value=new_post_value):
                self.assertEqual(new_post_value, form_value)

    def test_post_create_for_unknown(self):
        """Неавторизованный пользователь не может создать пост."""
        posts_count = Post.objects.count()
        form_data = {
            'author': self.user.username,
            'text': 'Текст формы неавторизованного пользователя',
            'group': self.group.id,
        }
        response = self.guest_client.post(
            self.CREATE_REV,
            data=form_data,
            follow=True
        )
        greate_to_login = f'{self.LOGIN_CREATE}?next={self.CREATE_REV}'
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, greate_to_login)

    def test_comment_creating_form(self):
        """Коментарий добавляется авторизованным пользователем."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Какой-то комментарий #1',
        }
        response = self.authorized_client.post(
            self.COMMENT_REV,
            data=form_data,
            follow=True
        )
        comment = Comment.objects.first()
        commeny_date = {
            comment.author: self.user,
            comment.post: self.post,
            comment.text: form_data['text']
        }
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        for new_comment, form_value in commeny_date.items():
            with self.subTest(new_comment=new_comment):
                self.assertEqual(new_comment, form_value)
