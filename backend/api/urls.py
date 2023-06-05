from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientsViewSet,
    RecipesViewSet,
    SubscribeViewSet,
    TagsViewSet
)

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
    RecipesViewSet,
    basename='recipes'
)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path(
        'users/subscriptions/',
        SubscribeViewSet.as_view({'get': 'list'}),
        name='author-subscribe'
    ),
    path(
        'users/<int:author_id>/subscribe/',
        SubscribeViewSet.as_view({
            'post': 'create',
            'delete': 'destroy'
        }),
        name='author-subscribe'
    ),
]
