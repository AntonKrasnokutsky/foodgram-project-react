from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class FoodgramUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    username = models.CharField(
        unique=True,
        max_length=150,
        validators=[validators.RegexValidator(regex=r'^[\w.@+-]')],
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
    )
    first_name = models.CharField(
        max_length=150,
        default='',
    )
    last_name = models.CharField(
        max_length=150,
        default=''
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.username}'
