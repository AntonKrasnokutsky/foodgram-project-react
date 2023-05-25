import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from recipes.models import (Ingredients, Favorites, RecipeIngredients, Recipes,
                            RecipesTag, Tags, Subscriptions, ShoppingCart)
from rest_framework import serializers

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        ]

    def get_is_subscribed(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if user is None or user.is_anonymous:
            return False
        author = get_object_or_404(User, username=obj.username)
        return author.subscriber.filter(
            user=user
        ).exists()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['id', 'name', 'color', 'slug']


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ['id', 'name', 'measurement_unit', ]


class AmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredients
        fields = '__all__'


class RecepiesIngredientsSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'name', 'measurement_unit', 'amount', ]


class RecepiesSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    # Не нашел как написать валидатор для поля tags, если убрать
    # read_only=True получаю ошибку "Недопустимые данные. Ожидался dictionary,
    # но был получен int." Изменение валидатора поля и валидатора объекта
    # результат не изменили
    tags = TagsSerializer(read_only=True, many=True)
    ingredients = RecepiesIngredientsSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        ]

    def get_recipe(self, obj):
        return get_object_or_404(Recipes, id=obj.id)

    def get_user(self):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        return user

    def get_is_favorited(self, obj):
        user = self.get_user()
        if user is None or user.is_anonymous:
            return False
        recipe = self.get_recipe(obj)
        return recipe.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.get_user()
        if user is None or user.is_anonymous:
            return False
        recipe = self.get_recipe(obj)
        return recipe.shopping_cart.filter(user=user).exists()

    def validate_ingredients(self, value, *args, **kwargs):
        ingredients = self.initial_data.get('ingredients')
        value = []
        ingridient = {}
        for recipe_ingredient in ingredients:
            if ('id' not in recipe_ingredient
                    or 'amount' not in recipe_ingredient):
                raise serializers.ValidationError('Отсутствуют ожидаемые поля '
                                                  '"id" или "amount".')
            if (not isinstance(recipe_ingredient['id'], int)
                    or not isinstance(recipe_ingredient['amount'], int)):
                raise serializers.ValidationError('Значение полей "id" и '
                                                  '"amount" дожно быть целое '
                                                  'число.')
            ingridient['id'] = recipe_ingredient['id']
            ingridient['amount'] = recipe_ingredient['amount']
            value.append(ingridient)
        return value

    def add_recipe_tags(self, recipe, tags, *args, **kwargs):
        for tag in tags:
            tag = get_object_or_404(Tags, pk=tag)
            RecipesTag.objects.create(recipe=recipe, tag=tag)

    def add_recipe_ingridients(self, recipe, ingredients, *args, **kwargs):
        for recipe_ingredient in ingredients:
            ingredient = get_object_or_404(
                Ingredients,
                pk=recipe_ingredient['id']
            )
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=recipe_ingredient['amount']
            )

    def create(self, *args, **kwargs):
        tags = self.initial_data.get('tags')
        if not all(map(lambda x: isinstance(x, int), tags)):
            raise serializers.ValidationError('Элементы дожны быть целыми '
                                              'числами.')
        ingredients = self.validated_data.pop('ingredients')
        author = self.get_user()
        recipe = Recipes.objects.create(**self.validated_data, author=author)

        self.add_recipe_tags(recipe, tags)
        self.add_recipe_ingridients(recipe, ingredients)

        return recipe

    def update(self, *args, **kwargs):
        tags = self.initial_data.get('tags')
        if not all(map(lambda x: isinstance(x, int), tags)):
            raise serializers.ValidationError('Элементы дожны быть целыми '
                                              'числами.')
        ingredients = self.validated_data.pop('ingredients')
        super().update(
            instance=self.instance,
            validated_data=self.validated_data
        )

        recipe_tags = list(RecipesTag.objects.filter(recipe=self.instance.id))

        for tag in tags:
            for recipe_tag in recipe_tags:
                if tag == recipe_tag.tag.id:
                    tags.remove(tag)
                    recipe_tags.remove(recipe_tag)
                    break

        for recipe_tag in recipe_tags:
            recipe_tag.delete()

        self.add_recipe_tags(self.instance, tags)

        recipe_ingredients = list(
            RecipeIngredients.objects.filter(
                recipe=self.instance.id
            ))

        for ingredient in ingredients:
            for recipe_ingredient in recipe_ingredients:
                if ingredient['id'] == recipe_ingredient.ingredient.id:
                    ingredients.remove(ingredient)
                    recipe_ingredients.remove(recipe_ingredient)
                    break

        for recipe_ingredient in recipe_ingredients:
            recipe_ingredient.delete()

        self.add_recipe_ingridients(self.instance, ingredients)

        return self.instance


class FavoritesSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.StringRelatedField(source='recipe.name')
    image = Base64ImageField(
        required=False,
        allow_null=True,
        source='recipe.image'
    )
    cooking_time = serializers.SerializerMethodField()

    class Meta:
        model = Favorites
        fields = ['id', 'name', 'image', 'cooking_time', ]
        read_only_fields = ['id', 'name', 'image', 'cooking_time', ]

    def get_id(self, obj):
        return obj.recipe.id

    def get_cooking_time(self, obj):
        return obj.recipe.cooking_time


class RecepiesSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = [
            'id',
            'name',
            'image',
            'cooking_time',
        ]


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True, source='author.email')
    id = serializers.IntegerField(read_only=True, source='author.id')
    username = serializers.StringRelatedField(source='author.username')
    first_name = serializers.StringRelatedField(source='author.first_name')
    last_name = serializers.StringRelatedField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecepiesSubscribeSerializer(
        read_only=True,
        many=True,
        source='author.recipes'
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscriptions
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]
        read_only_fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]

    def get_is_subscribed(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if user is None or user.is_anonymous:
            return False
        author = get_object_or_404(User, username=obj.author.username)
        return author.subscriber.filter(
            user=user
        ).exists()

    def get_recipes_count(self, obj):
        return obj.author.recipes.all().count()


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, source='recipe.id')
    name = serializers.StringRelatedField(source='recipe.name')
    image = Base64ImageField(
        required=False,
        allow_null=True,
        source='recipe.image'
    )
    cooking_time = serializers.IntegerField(read_only=True, source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'image', 'cooking_time', ]
        read_only_fields = ['id', 'name', 'image', 'cooking_time', ]
