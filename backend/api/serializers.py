import base64
import numbers

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (
    Favorites,
    Ingredients,
    RecipeIngredients,
    Recipes,
    RecipesTag,
    ShoppingCart,
    Subscriptions,
    Tags
)

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
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
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
            format, image_string = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(image_string),
                name=f'temp.{ext}'
            )
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


class RecipeTagsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tag.id')
    name = serializers.StringRelatedField(source='tag.name')
    color = serializers.StringRelatedField(source='tag.color')
    slug = serializers.SlugField(source='tag.slug')

    class Meta:
        model = RecipesTag
        fields = ['id', 'name', 'color', 'slug']


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
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
    ingredients = RecipeIngredientsSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (
            'view' in self.context
            and self.context['view'].action not in ('create', 'partial_update')
        ):
            self.fields.update({'tags': RecipeTagsSerializer(many=True)})

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

    def __current_user(self):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return request.user
        return None

    def get_is_favorited(self, obj):
        user = self.__current_user()
        if user is None or user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.__current_user()
        if user is None or user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=user).exists()

    def validate_ingredients(self, value, *args, **kwargs):
        ingredients = self.initial_data.get('ingredients')
        value = []
        for recipe_ingredient in ingredients:
            ingridient = {}
            if 'id' not in recipe_ingredient:
                raise serializers.ValidationError(
                    'Отсутствуют ожидаемые поля "id".'
                )
            if 'amount' not in recipe_ingredient:
                raise serializers.ValidationError(
                    'Отсутствуют ожидаемые поля "amount".'
                )
            if not isinstance(recipe_ingredient['id'], numbers.Number):
                raise serializers.ValidationError(
                    'Значение полей "id" дожно быть числом.'
                )
            if not isinstance(recipe_ingredient['amount'], numbers.Number):
                raise serializers.ValidationError(
                    'Значение полей "amount" дожно быть числом.'
                )
            ingridient['id'] = recipe_ingredient['id']
            ingridient['amount'] = recipe_ingredient['amount']
            value.append(ingridient)
        return value

    def validate_tags(self, value, *args, **kwargs):
        tags = self.initial_data.get('tags')
        if not all(map(lambda x: isinstance(x, int), tags)):
            raise serializers.ValidationError(
                'Элементы дожны быть целыми числами.'
            )
        return tags

    def __add_recipe_tags(self, recipe, tags, *args, **kwargs):
        for tag in tags:
            tag = get_object_or_404(Tags, pk=tag)
            RecipesTag.objects.create(recipe=recipe, tag=tag)

    def __add_recipe_ingridients(self, recipe, ingredients, *args, **kwargs):
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

    def validate(self, attrs):
        self.fields.update({"tags": RecipeTagsSerializer(many=True)})
        return super().validate(attrs)

    def create(self, *args, **kwargs):
        tags = self.validated_data.pop('tags')
        ingredients = self.validated_data.pop('ingredients')
        author = self.__current_user()
        recipe = Recipes.objects.create(**self.validated_data, author=author)

        self.__add_recipe_tags(recipe, tags)
        self.__add_recipe_ingridients(recipe, ingredients)

        return recipe

    def update(self, *args, **kwargs):
        tags = self.validated_data.pop('tags')
        ingredients = self.validated_data.pop('ingredients')
        super().update(
            instance=self.instance,
            validated_data=self.validated_data
        )

        recipe_tags = list(RecipesTag.objects.filter(recipe=self.instance.id))

        for recipe_tag in recipe_tags:
            if recipe_tag.tag.id in tags:
                tags.remove(recipe_tag.tag.id)
                recipe_tags.remove(recipe_tag)

        RecipesTag.objects.filter(
            pk__in=map(lambda tag: tag.id, recipe_tags)
        ).delete()

        self.__add_recipe_tags(self.instance, tags)

        recipe_ingredients = list(
            RecipeIngredients.objects.filter(
                recipe=self.instance.id
            ))
        for recipe_ingredient in recipe_ingredients:
            ingredient = next(
                (
                    ingredient for ingredient in ingredients if (
                        ingredient["id"] == recipe_ingredient.ingredient.id
                    )
                ),
                False
            )
            if ingredient:
                ingredients.remove(ingredient)
                recipe_ingredients.remove(recipe_ingredient)

        RecipeIngredients.objects.filter(
            pk__in=map(lambda ingredient: ingredient.id, recipe_ingredients)
        ).delete()

        self.__add_recipe_ingridients(self.instance, ingredients)

        return self.instance


class FavoritesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='recipe.id')
    name = serializers.StringRelatedField(source='recipe.name')
    image = Base64ImageField(
        required=False,
        allow_null=True,
        source='recipe.image'
    )
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')

    class Meta:
        model = Favorites
        fields = ['id', 'name', 'image', 'cooking_time', ]
        read_only_fields = ['id', 'name', 'image', 'cooking_time', ]


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
    name = serializers.StringRelatedField(read_only=True, source='recipe.name')
    image = Base64ImageField(
        read_only=True,
        required=False,
        allow_null=True,
        source='recipe.image'
    )
    cooking_time = serializers.IntegerField(
        read_only=True,
        source='recipe.cooking_time'
    )

    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'image', 'cooking_time', ]
        read_only_fields = ['id', 'name', 'image', 'cooking_time', ]
