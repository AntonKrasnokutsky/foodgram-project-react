from django.urls import include, path
from rest_framework import routers

from .views import IngredientsViewStet, TagsViewStet

router = routers.DefaultRouter()
router.register(
    'tags',
    TagsViewStet,
    basename='tags'
)
router.register(
    'ingredients',
    IngredientsViewStet,
    basename='ingredients'
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
    path('', include(router.urls)),
]
