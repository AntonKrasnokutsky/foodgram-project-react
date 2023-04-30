from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    username = models.CharField(
        unique=False,
        max_length=150,
        null=True,
        blank=True,
        validators=[validators.RegexValidator(regex=r'^[\w.@+-]')],
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        blank=False,
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        default='',
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        default=''
    )

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' ' + self.username
