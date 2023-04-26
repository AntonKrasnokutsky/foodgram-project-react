from django.conf import settings as s
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsAdmin
from .serializers import TokenSerializer, SignUpSerializer, UserSerializer


class SignUpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, create = User.objects.get_or_create(
                **serializer.validated_data
            )
        except IntegrityError:
            return Response(
                'Извините, этот адрес электронной почты или'
                ' имя пользователя уже существует.',
                status=status.HTTP_400_BAD_REQUEST
            )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Ваш код подтверждения здесь:',
            f'{confirmation_code}',
            s.EMAIL_ADDRESS,
            [serializer.validated_data.get('email')],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data.get('username')
        )
        if not default_token_generator.check_token(
            user, request.data.get('confirmation_code')
        ):
            return Response(
                'Токен недействителен',
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {'access': str(refresh.access_token)},
            status=status.HTTP_200_OK,
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAdmin, ]
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['username', ]
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @action(
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=[IsAuthenticated, ],
        detail=False,
    )
    def user_profile(self, request):
        if request.method == 'PATCH':
            serializer = self.serializer_class(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserSerializer
    http_method_names = ['post', ]

    def post(self, *args, **kwargs):
        self.request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
