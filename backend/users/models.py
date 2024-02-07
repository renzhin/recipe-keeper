from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.validators import validate_me, username_validator


class ModifiedUser(AbstractUser):

    email = models.EmailField(
        'Электронная почта',
        unique=True,
        max_length=254,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[validate_me, username_validator]
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True,
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Follow(models.Model):
    follower = models.ForeignKey(
        ModifiedUser, on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='following',
        verbose_name='подписчик',
    )
    following = models.ForeignKey(
        ModifiedUser, on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='followers',
        verbose_name='на кого подписан',
    )

    def __str__(self):
        return f"{self.follower} подписан на {self.following}"

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
