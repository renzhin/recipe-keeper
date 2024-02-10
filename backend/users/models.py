from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.validators import validate_me, username_validator
from foodgram_backend.constants import (
    EMAIL_NUMBCHAR,
    USER_FIELDS_NUMBCHAR
)


class ModifiedUser(AbstractUser):

    email = models.EmailField(
        unique=True,
        max_length=EMAIL_NUMBCHAR,
        verbose_name='Электронная почта',
    )
    username = models.CharField(
        max_length=USER_FIELDS_NUMBCHAR,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[validate_me, username_validator]
    )
    first_name = models.CharField(
        max_length=USER_FIELDS_NUMBCHAR,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=USER_FIELDS_NUMBCHAR,
        blank=True,
        verbose_name='Фамилия',
    )
    password = models.CharField(
        max_length=USER_FIELDS_NUMBCHAR,
        verbose_name='Пароль',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )
    USERNAME_FIELD = 'email'


class Follow(models.Model):
    follower = models.ForeignKey(
        ModifiedUser, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='подписчик',
    )
    following = models.ForeignKey(
        ModifiedUser, on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='на кого подписан',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

        constraints = (
            models.UniqueConstraint(
                fields=(
                    'follower',
                    'following'
                ),
                name='uniq_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F(
                    'following')
                ),
                name='stop_me',
            ),
        )

    def __str__(self):
        return f'{self.follower} подписан на {self.following}'
