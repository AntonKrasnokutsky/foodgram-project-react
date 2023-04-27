from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core import validators


class User(AbstractUser):
    username = models.CharField(
        unique=True,
        max_length=150,
        null=False,
        blank=False,
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
