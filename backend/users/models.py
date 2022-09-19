from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    email = models.EmailField(
        'email address',
        max_length=254,
        unique=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
        help_text='Данный пользователь станет подписчиком автора',
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name="Автор",
        on_delete=models.CASCADE,
        help_text='На автора могут подписаться другие пользователи',
    )

    class Meta:
        ordering = ('-id',)
        constraints = (
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
