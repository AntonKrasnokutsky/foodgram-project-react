import json
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()
client = APIClient()


class UsersTestCase(TestCase):
    def test_guest_users(self):
        data = {
            "email": "vpupkin@yande.ru",
            "username": "vasya.pupkn",
            "first_name": "Вас",
            "last_name": "Пупки",
            "password": "Qwerty12"
        }
        request = client.post('/api/users/', data)
        print(request.data)
