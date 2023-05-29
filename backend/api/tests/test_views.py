import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipes.models import Tags, Ingredients
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()
client = APIClient()


class GuestUsersTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(
            email='a@a.ru',
            username='test_user',
            first_name='test_first_name',
            last_name='test_last_name',
            password='testPassword123',
        )
        tag = Tags.objects.create(
            name='Тег1',
            color='#aabbcc',
            slug='tag1',
        )
        cls.tag1 = {
            'id': tag.id,
            'name': 'Тег1',
            'color': '#aabbcc',
            'slug': 'tag1',
        }
        tag = Tags.objects.create(
            name='Тег2',
            color='#ddeeff',
            slug='tag2',
        )
        cls.tag2 = {
            'id': tag.id,
            'name': 'Тег2',
            'color': '#ddeeff',
            'slug': 'tag2',
        }
        tag = Tags.objects.create(
            name='Тег3',
            color='#112233',
            slug='tag3',
        )
        cls.tag3 = {
            'id': tag.id,
            'name': 'Тег3',
            'color': '#112233',
            'slug': 'tag3',
        }

        ingredient = Ingredients.objects.create(
            name='Ингридиент 1',
            measurement_unit='кг.'
        )
        cls.ingredient1 = {
            'id': ingredient.id,
            'name': 'Ингридиент 1',
            'measurement_unit': 'кг.',
        }
        ingredient = Ingredients.objects.create(
            name='Ингридиент 2',
            measurement_unit='шт.'
        )
        cls.ingredient2 = {
            'id': ingredient.id,
            'name': 'Ингридиент 2',
            'measurement_unit': 'шт.',
        }

    def test_guest_user_registrate(self):
        path = '/api/users/'
        data = {
            'email': 'vpupkin@yande.ru',
            'username': 'vasya.pupkn',
            'first_name': 'Вася',
            'last_name': 'Пупки',
            'password': 'Qwerty12'
        }
        request = client.post(path, data)
        user = User.objects.last()
        data_request = {
            'email': 'vpupkin@yande.ru',
            'username': 'vasya.pupkn',
            'first_name': 'Вася',
            'last_name': 'Пупки',
            'id': user.id
        }
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        for field, value in data_request.items():
            with self.subTest(value=value):
                self.assertEqual(request.data[field], value)

    def test_guest_user_get_user_profile(self, *args, **kwargs):
        path = f'/api/users/{self.test_user.id}/'
        request = client.get(path)
        data_request = {
            "email": self.test_user.email,
            "id": self.test_user.id,
            "username": self.test_user.username,
            "first_name": self.test_user.first_name,
            "last_name": self.test_user.last_name,
            "is_subscribed": False
        }
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        for field, value in data_request.items():
            with self.subTest(value=value):
                self.assertEqual(request.data[field], value)

    def test_guest_user_get_tags_list(self, *args, **kwargs):
        path = '/api/tags/'
        request = client.get(path)

        self.assertEqual(request.status_code, status.HTTP_200_OK)
        data_request = [self.tag1, self.tag2, self.tag3]
        self.assertEqual(request.data, data_request)

    def test_guest_user_get_tag(self, *args, **kwargs):
        path = f'/api/tags/{self.tag1["id"]}/'
        request = client.get(path)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.data, self.tag1)

    def test_guest_user_get_ingredients_list(self, *args, **kwargs):
        path = '/api/ingredients/'
        request = client.get(path)

        self.assertEqual(request.status_code, status.HTTP_200_OK)
        data_request = [self.ingredient1, self.ingredient2]
        self.assertEqual(request.data, data_request)

    def test_guest_user_get_ingredient(self, *args, **kwargs):
        path = f'/api/ingredients/{self.ingredient1["id"]}/'
        request = client.get(path)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.data, self.ingredient1)
