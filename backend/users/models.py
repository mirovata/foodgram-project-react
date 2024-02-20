from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from core.constants import LENGTH, LENGTH_EMAIL


class User(AbstractUser):
    """Пользовательская модель."""

    email = models.EmailField(
      max_length=LENGTH_EMAIL,
      unique=True,
      verbose_name='Почта'
    )
    username = models.CharField(
        max_length=LENGTH,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[\ \w.@+-]+$')
        ],
        verbose_name='Логин'
    )
    first_name = models.CharField(
        max_length=LENGTH,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=LENGTH,
        verbose_name='Фамилия пользователя'
    )
    password = models.CharField(
        max_length=LENGTH,
        verbose_name='Пароль'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password'
    ]

    class Meta:

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class UserSubscribe(models.Model):
    """Модель для подписок."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Отслеживаемый человек'
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписчик'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата подписки.',
        auto_now_add=True
    )

    class Meta:

        verbose_name = 'Пользовательскую подписку'
        verbose_name_plural = 'Пользовательские подписки'
        constraints = (
            models.UniqueConstraint(fields=('author', 'follower', ),
                                    name='unique_follow'),
        )
        ordering = ['-pub_date']

    def __str__(self):
        return '{followers} подписан на {following}'.format(
            followers=self.follower.username,
            following=self.author.username,
        )
