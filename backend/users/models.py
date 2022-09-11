from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin


class User(AbstractUser, PermissionsMixin):

    email = models.EmailField(
        verbose_name='Email',
        max_length=128,
        unique=True,
        help_text='Ваша электронная почта. Длина не более 128 символов',
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=128,
        unique=True,
        help_text='Логин длиной не более 128 символов',
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=128,
        help_text='Пароль длиной не более 128 символов',
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=128,
        help_text='Ваше имя. Длина не более 128 символов',
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=128,
        help_text='Фамилия. Длина не более 128 символов',
    )
    is_superuser = models.BooleanField(
        verbose_name='Права администратора',
        default=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'password')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='На автора могут подписаться другие пользователи',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Подписаться на автора',
    )

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='unique_follow',
            ),
        )

    def __str__(self):
        return f'{self.user}-->@{self.author}'
