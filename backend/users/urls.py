from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, SignUpView, GetTokenView, LogoutViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/token/login/', GetTokenView.as_view(), name='get_token'),
    path('auth/token/logout/', LogoutViewSet.as_view(), name='logout'),
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('', include(router.urls)),
]
