from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorites, Ingredients, Recipes, Tags
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination

from .serializers import (FavoritesSerializer, IngredientsSerializer,
                          RecepiesSerializer, SubscribeSerializer,
                          TagsSerializer)

User = get_user_model()


class IngredientsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['name', ]


class TagsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class FavoritesViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = FavoritesSerializer
    pagination_class = None

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.request.user)
        return user.favorites.all()

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipes, pk=self.kwargs.get('recipe_id'))
        if Favorites.objects.filter(
            recipe=recipe,
            user=self.request.user
        ).exists():
            data = {
                'error': 'Рецепт уже в избранном.'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        if not serializer.is_valid():
            return super().permission_denied(self.request)

        recipe = get_object_or_404(Recipes, pk=self.kwargs.get('recipe_id'))
        serializer.save(recipe_id=recipe.id, user_id=self.request.user.id)

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipes, pk=self.kwargs.get('recipe_id'))
        try:
            favorite = Favorites.objects.get(
                recipe=recipe,
                user=self.request.user
            )
            favorite.delete()
        except Favorites.DoesNotExist:
            data = {
                'error': 'Рецепта нет в избранном.'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({}, status=HTTPStatus.NO_CONTENT)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecepiesSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author', )    # 'tags')


class SubscribeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pagination_class = LimitOffsetPagination
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.request.user)
        return user.publisher.all()
