from rest_framework import serializers
from django.core.validators import RegexValidator

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(f"Name '{value}' is forbidden")
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(regex=r'^[\w.@+\- ]+$')],
        required=True,
    )
    confirmation_code = serializers.CharField(max_length=None, required=True)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(f"Name '{value}' is forbidden")
        return value
