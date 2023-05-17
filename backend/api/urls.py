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

router.register(
    r'users/((?P<user_id>\d+))/subscribe',
    SubscribeViewSet,
    basename='subscribe'
)

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscribeViewSet.as_view({'get': 'list'})
    ),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoritesViewSet.as_view({
            'post': 'create',
            'delete': 'destroy'
        })),
    path('', include(router.urls)),
]
