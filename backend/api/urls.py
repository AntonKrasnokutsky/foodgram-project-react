from django.urls import include, path
from rest_framework import routers

from .views import FavoritesViewSet, IngredientsViewSet, RecipesViewSet, TagsViewSet

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


# router.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet,
#     basename='comments'
# )
# router.register('titles', TittleViewSet, basename='Title')
# router.register('genres', GenreViewSet, basename='Genre')
# router.register('categories', CategoryViewSet, basename='Category')

urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/', FavoritesViewSet.as_view({'post': 'create', 'delete': 'destroy'})),
    path('', include(router.urls)),
]
