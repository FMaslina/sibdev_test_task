from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password')

    def validate_email(self, value):    # Проверяем почту на уникальность
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Пользователь с такой почтой уже существует')
        return value

    def create(self, validated_data):   # Создаем юзера
        return User.objects.create_user(**validated_data)


class TokenAuthSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['id'] = user.id
        token['email'] = user.email
        token['username'] = user.username

        return token
