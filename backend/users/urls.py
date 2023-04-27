from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GetTokenView, LogoutViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/token/login/', GetTokenView.as_view(), name='get_token'),
    path(
        'auth/token/logout/',
        LogoutViewSet.as_view({'post': 'logout'}),
        name='logout'
    ),
    path('', include(router.urls)),
]
