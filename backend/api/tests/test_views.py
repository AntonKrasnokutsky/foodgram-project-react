from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from recipes.models import (Ingredients, RecipeIngredients, Recipes,
                            RecipesTag, Tags)

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
        cls.author = {
            'email': 'a@a.ru',
            'username': 'test_user',
            'first_name': 'test_first_name',
            'last_name': 'test_last_name',
            'is_subscribed': False,
        }
        tag1 = Tags.objects.create(
            name='Тег1',
            color='#aabbcc',
            slug='tag1',
        )
        cls.tag1 = {
            'id': tag1.id,
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

        ingredient1 = Ingredients.objects.create(
            name='Ингридиент 1',
            measurement_unit='кг.'
        )
        cls.ingredient1 = {
            'id': ingredient1.id,
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
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.recipe_obj = Recipes.objects.create(
            author=cls.test_user,
            name='Тестоый рецепт',
            image=cls.uploaded,
            text='Описание тестового рецепта',
            cooking_time=1
        )
        RecipesTag.objects.create(
            recipe=cls.recipe_obj,
            tag=tag1,
        )
        recipe_ingredient = RecipeIngredients.objects.create(
            recipe=cls.recipe_obj,
            ingredient=ingredient1,
            amount=1,
        )
        cls.recipe = {
            'id': cls.recipe_obj.id,
            'tags': [
                {
                    'id': tag1.id,
                    'name': 'Тег1',
                    'color': '#aabbcc',
                    'slug': 'tag1',
                },
            ],
            'author': cls.author,
            'ingredients': [
                {
                    'id': ingredient1.id,
                    'name': ingredient1.name,
                    'measurement_unit': ingredient1.measurement_unit,
                    'amount': recipe_ingredient.amount
                }
            ],
            "is_favorited": False,
            "is_in_shopping_cart": False,
            "name": cls.recipe_obj.name,
            "image": cls.recipe_obj.image,
            "text": cls.recipe_obj.text,
            "cooking_time": cls.recipe_obj.cooking_time
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

    def test_guest_user_get_recipes_list(self, *args, **kwargs):
        path = '/api/recipes/'
        request = client.get(path)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    # def test_guest_user_get_recipe(self, *args, **kwargs):
    #     path = f'/api/recipes/{self.recipe_obj.id}/'
    #     request = client.get(path)
    #     self.assertEqual(request.status_code, status.HTTP_200_OK)
    #     self.assertEqual(request.data, self.recipe)

    def test_guest_user_unauthorized_error_post(self, *args, **kwargs):
        paths_post = [
            '/api/recipes/',
            f'/api/recipes/{self.recipe_obj.id}/shopping_cart/',
            f'/api/recipes/{self.recipe_obj.id}/favorite/',
            f'/api/users/{self.test_user.id}/subscribe/',
        ]
        for path in paths_post:
            request = client.post(path)
            self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_guest_user_unauthorized_error_delete(self, *args, **kwargs):
        paths_post = [
            f'/api/recipes/{self.recipe_obj.id}/',
            f'/api/recipes/{self.recipe_obj.id}/shopping_cart/',
            f'/api/recipes/{self.recipe_obj.id}/favorite/',
            f'/api/users/{self.test_user.id}/subscribe/',
        ]
        for path in paths_post:
            request = client.delete(path)
            self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_guest_user_unauthorized_error_patch(self, *args, **kwargs):
        path = f'/api/recipes/{self.recipe_obj.id}/'
        request = client.patch(path)
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_guest_user_unauthorized_error_get(self, *args, **kwargs):
        paths_post = [
            '/api/recipes/download_shopping_cart/',
            '/api/users/subscriptions/',
        ]
        for path in paths_post:
            request = client.get(path)
            self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)
