from django.urls import include, path
from rest_framework import routers

from .views import (FavoritesViewSet, IngredientsViewSet, RecipesViewSet,
                    SubscribeViewSet, TagsViewSet)

router = routers.DefaultRouter()
router.register(
    'tags',
    TagsViewSet
)
router.register(
    'ingredients',
    IngredientsViewSet
)
router.register(
    'recipes',
    RecipesViewSet
)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'users/subscriptions/',
        SubscribeViewSet.as_view({'get': 'list'})
    ),
    path(
        'users/<int:author_id>/subscribe/',
        SubscribeViewSet.as_view({
            'post': 'create',
            'delete': 'destroy'
        })),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoritesViewSet.as_view({
            'post': 'create',
            'delete': 'destroy'
        })),
]
