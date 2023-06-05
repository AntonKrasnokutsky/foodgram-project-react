import io
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination

from recipes.models import (
    Favorites,
    Ingredients,
    Recipes,
    ShoppingCart,
    Subscriptions,
    Tags
)
from .serializers import (
    FavoritesSerializer,
    IngredientsSerializer,
    RecepiesSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    TagsSerializer
)

User = get_user_model()


class IngredientsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('@name',)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)


class TagsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecepiesSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author', )

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'shopping_cart':
            return ShoppingCartSerializer
        if self.action == 'favorite':
            return FavoritesSerializer
        return self.serializer_class

    @property
    def get_ingridients(self, *args, **kwargs):
        recipes = self.request.user.shopping_cart.filter()
        ingredients = {}
        for recipe in recipes:
            for recipe_ingredient in recipe.recipe.ingredients.all():
                if recipe_ingredient.ingredient in ingredients:
                    ingredients[
                        recipe_ingredient.ingredient
                    ] += recipe_ingredient.amount
                else:
                    ingredients[
                        recipe_ingredient.ingredient
                    ] = recipe_ingredient.amount
        return ingredients

    @property
    def recipe(self):
        return get_object_or_404(Recipes, pk=self.kwargs.get('pk'))

    def create_txt(self, ingredients, *args, **kwargs):
        text_file = io.StringIO()
        for ingredient, amount in ingredients.items():
            text = (f'{ingredient.name}, '
                    f'{ingredient.measurement_unit}: {amount}')
            text_file.write(text)
            text_file.write('\n')
        value = text_file.getvalue()
        text_file.close()
        return value

    @action(methods=['get'], detail=False, url_path=r'download_shopping_cart')
    def download_shopping_cart(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            data = {
                'detail': 'Учетные данные не были предоставлены.'
            }
            return JsonResponse(data, status=status.HTTP_401_UNAUTHORIZED)
        text_file = self.create_txt(self.get_ingridients)
        file_name = f'{self.request.user.username}shopping_cart.txt'
        response = HttpResponse(text_file, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

    @action(
        methods=['post', 'delete'],
        serializer_class=ShoppingCartSerializer,
        detail=True,
        url_path='shopping_cart'
    )
    def shopping_cart(self, *args, **kwargs):
        if self.request.method == 'POST':
            if ShoppingCart.objects.filter(
                recipe=self.recipe,
                user=self.request.user
            ).exists():
                data = {
                    'error': 'Рецепт уже в списке покупок.'
                }
                return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
            serializer = self.get_serializer(data=self.request.data)
            if not serializer.is_valid():
                return super().permission_denied(self.request)
            serializer.save(
                recipe_id=self.recipe.id,
                user_id=self.request.user.id
            )
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        try:
            shopping_cart = ShoppingCart.objects.get(
                recipe=self.recipe,
                user=self.request.user
            )
            shopping_cart.delete()
        except ShoppingCart.DoesNotExist:
            data = {
                'error': 'Рецепта нет в списке покупок.'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({}, status=HTTPStatus.NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        serializer_class=FavoritesSerializer,
        permission_classes=[permissions.IsAuthenticated, ],
        detail=True,
        url_path='favorite'
    )
    def favorite(self, *args, **kwargs):
        if self.request.method == 'POST':
            if Favorites.objects.filter(
                recipe=self.recipe,
                user=self.request.user
            ).exists():
                data = {
                    'error': 'Рецепт уже в избранном.'
                }
                return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
            serializer = self.get_serializer(data=self.request.data)
            if not serializer.is_valid():
                return super().permission_denied(self.request)
            serializer.save(
                recipe_id=self.recipe.id,
                user_id=self.request.user.id
            )
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        try:
            favorite = Favorites.objects.get(
                recipe=self.recipe,
                user=self.request.user
            )
            favorite.delete()
        except Favorites.DoesNotExist:
            data = {
                'error': 'Рецепта нет в избранном.'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({}, status=HTTPStatus.NO_CONTENT)


class SubscribeViewSet(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    serializer_class = SubscribeSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        return self.request.user.publisher.all()

    @property
    def author(self):
        return get_object_or_404(User, pk=self.kwargs.get('author_id'))

    def create(self, request, *args, **kwargs):
        if self.author == self.request.user:
            data = {
                'error': 'Нельзя подписаться на себя..'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)

        if Subscriptions.objects.filter(
            author=self.author,
            user=self.request.user
        ).exists():
            data = {
                'error': 'Подписка на автора активна.'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        if not serializer.is_valid():
            return super().permission_denied(self.request)

        serializer.save(author=self.author, user=self.request.user)
        return None

    def destroy(self, request, *args, **kwargs):
        try:
            subscriptions = Subscriptions.objects.get(
                author=self.author,
                user=self.request.user
            )
            subscriptions.delete()
        except Subscriptions.DoesNotExist:
            data = {
                'error': 'Вы не подписаны на автора.'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({}, status=HTTPStatus.NO_CONTENT)
