from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, Q

from users.constants import (
    EMAIL_FIELD_LENGTH,
)


class User(AbstractUser):

    email = models.EmailField(
        max_length=EMAIL_FIELD_LENGTH,
        unique=True,
        null=False,
        blank=False,
        verbose_name='Email addres'
    )
    # is_subscribed = models.BooleanField(
    #     default=False,
    #     verbose_name="Is subscribed"
    # )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        default=None,
        verbose_name='Avatar'
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            CheckConstraint(
                check=~Q(username='me'), name='username_me_banned_word'
            )
        ]
        ordering = ('email',)

    def __str__(self) -> str:
        return self.username
