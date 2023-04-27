# from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import AuthorOrAdminOrReadOnly
from .serializers import TokenSerializer, UserSerializer


class GetTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data.get('username')
        )

        refresh = RefreshToken.for_user(user)
        return Response(
            {'access': str(refresh.access_token)},
            status=status.HTTP_200_OK,
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['username', 'email', ]
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny, ]
        else:
            permission_classes = [AuthorOrAdminOrReadOnly]
        return [permission() for permission in permission_classes]

    # def update(self, request, *args, **kwargs):
    #     return super().update(request, *args, **kwargs)

    # @action(
    #     methods=['get', 'patch'],
    #     url_path='me',
    #     permission_classes=[IsAuthenticated, ],
    #     detail=False,
    # )
    # def user_profile(self, request):
    #     if request.method == 'PATCH':
    #         serializer = self.serializer_class(
    #             request.user,
    #             data=request.data,
    #             partial=True
    #         )
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     serializer = self.serializer_class(request.user)
    #     return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    # serializer_class = UserSerializer
    http_method_names = ['post', ]

    @action(detail=True, methods=['post'])
    def logout(self, *args, **kwargs):
        self.request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
