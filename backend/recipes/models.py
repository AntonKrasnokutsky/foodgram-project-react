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

    class Meta:
        ordering = ['name', ]
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self, *args, **kwargs):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(max_length=100, verbose_name='Ингридиент')
    measurement_unit = models.CharField(
        max_length=100,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['name', ]
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self, *args, **kwargs):
        return self.name


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='publisher',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ['author', 'user', ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    name = models.CharField(max_length=100, verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.SmallIntegerField(
        verbose_name='Время приготовления (минут)'
    )
    tags = models.ManyToManyField(Tags, through='RecipesTag')

    class Meta:
        ordering = ['name', ]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self, *args, **kwargs):
        return self.name


class RecipesTag(models.Model):
    recipe = models.ForeignKey('Recipes', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tags', on_delete=models.CASCADE)

    class Meta:
        ordering = ['recipe', ]
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'

    def __str__(self, *args, **kwargs):
        return self.tag.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        'Recipes',
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    ingredient = models.ForeignKey(
        'Ingredients',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField()

    class Meta:
        ordering = ['recipe', 'ingredient', ]
        verbose_name = 'Ингридиент рецепта'
        verbose_name_plural = 'Ингридиенты рецептов'

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

    class Meta:
        ordering = ['recipe', ]
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'

    def __str__(self, *args, **kwargs):
        return self.recipe.name


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        'Recipes',
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )

    class Meta:
        ordering = ['recipe', ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списоки покупок'

    def __str__(self, *args, **kwargs):
        return self.recipe.name
