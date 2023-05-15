from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth import get_user_model

from recipes.models import Favorites, Ingredients, Recipes, Tags
from .serializers import (
    FavoritesSerializer,
    IngredientsSerializer,
    RecepiesSerializer,
    TagsSerializer,
)

User = get_user_model()


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    http_method_names = ['get', ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['name', ]


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    http_method_names = ['get', ]


class FavoritesViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = FavoritesSerializer
    pagination_class = None

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.request.user)
        return user.favorites.all()

    def perform_create(self, serializer):
        if not serializer.is_valid():
            return super().permission_denied(self.request)
        recipe = get_object_or_404(Recipes, pk=self.kwargs.get('recipe_id'))
        serializer.save(recipe_id=recipe.id, user_id=self.request.user.id)

        return super().perform_create(serializer)

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipes, pk=self.kwargs.get('recipe_id'))
        try:
            favorite = Favorites.objects.get(recipe=recipe, user=self.request.user)
            favorite.delete()
            
        except Favorites.DoesNotExist:
            pass
        # return super().destroy(request, *args, **kwargs)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecepiesSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author', )    # 'tags')
