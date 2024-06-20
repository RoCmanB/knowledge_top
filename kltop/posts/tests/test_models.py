from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, TEXT_LIMETER

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает str."""
        post = self.post
        expected_post_text = post.text[:TEXT_LIMETER]
        self.assertEqual(expected_post_text, str(post))

    def test_models_have_correct_object_names_group(self):
        """Проверяем, что у моделей корректно работает str."""
        group = self.group
        expected_group_text = group.title
        self.assertEqual(expected_group_text, str(group))

    # Дополнительное задание
    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Введите текст статьи',
            'pub_date': 'Date of pub',
            'author': 'Author',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_name(self):
        """help_text в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Не более 50000 символов',
            'pub_date': '',
            'author': '',
            'group': 'Одну из доступных',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
