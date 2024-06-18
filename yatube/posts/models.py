from django.db import models
from django.contrib.auth import get_user_model


TEXT_LIMETER = 15

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    """Django ORM for keeping informations about posts."""
    title = models.CharField(
        max_length=100,
        verbose_name='Название статьи',
        help_text='Введите текст названия статьи'
    )
    text = models.CharField(max_length=50000)
    pub_date = models.DateTimeField('Date of pub', auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Author')
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              related_name='posts',
                              verbose_name='Выберите группу',
                              help_text='Одну из доступных')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.text[:TEXT_LIMETER]


class Comment(models.Model):
    """Django ORM for kepping informations about
    comments for posts.
    """
    text = models.CharField(
        max_length=100,
        verbose_name='Ваш комментарий',
        help_text='Количество символов не более 100'
    )
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Post')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Author')
    created = models.DateTimeField('Date of create comment',
                                   auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]
