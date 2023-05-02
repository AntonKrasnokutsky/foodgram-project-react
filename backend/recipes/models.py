from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tags(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Тег'
    )
    color = models.CharField(max_length=7, unique=True, verbose_name='Цвет')
    slug = models.SlugField(unique=True)

    def __str__(self, *args, **kwargs):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(max_length=100, verbose_name='Ингридиент')
    measurement_unit = models.CharField(
        max_length=100,
        verbose_name='Единица измерения'
    )

    def __str__(self, *args, **kwargs):
        return self.name


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='publisher'
    )


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(max_length=100, verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        default=None
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.SmallIntegerField(
        verbose_name='Время приготовления (минут)'
    )

    def __str__(self, *args, **kwargs):
        return self.name


class RecipesTag(models.Model):
    recipe = models.ForeignKey('Recipes', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tags', on_delete=models.CASCADE)

    def __str__(self, *args, **kwargs):
        return self.tag.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey('Recipes', on_delete=models.CASCADE)
    ingredient = models.ForeignKey('Ingredients', on_delete=models.CASCADE)
    amount = models.FloatField()

    def __str__(self, *args, **kwargs):
        return self.ingredient.name


class Favorites(models.Model):
    recipe = models.ForeignKey(
        'Recipes',
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    def __str__(self, *args, **kwargs):
        return self.recipe.name
