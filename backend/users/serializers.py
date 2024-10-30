import re

from rest_framework import serializers
from djoser.serializers import UserSerializer as BaseUserSerializer
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.contrib.auth import get_user_model

from api.serializers import Base64ImageField
from api.constants import USERNAME_LENGTH
from users.constants import EMAIL_FIELD_LENGTH


User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class UserSerializer(BaseUserSerializer):
    email = serializers.EmailField(
        max_length=EMAIL_FIELD_LENGTH,
        required=True
    )
    username = serializers.CharField(
        max_length=USERNAME_LENGTH,
        required=True
    )
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 
                  'last_name', 'is_subscribed', 'avatar')
        read_only_filds = ('id',)

    def validate(self, attrs):
        if self.context['request'].method == 'PATCH':
            username = attrs.get('username')
            if username is not None and not re.match(r'^[\w.@+-]+$', username):
                raise serializers.ValidationError(
                    r'Username must match the pattern: ^[\w.@+-]+\Z'
                )
            if 'username' not in attrs or 'email' not in attrs:
                return attrs
        return super().validate(attrs)



class SignUpSerializer(BaseUserCreateSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        max_length=EMAIL_FIELD_LENGTH,
        required=True
    )
    username = serializers.CharField(
        max_length=USERNAME_LENGTH,
        required=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def validate_email(self, value):
        existing_user = User.objects.filter(email=value).first()
        if existing_user and existing_user.username != self.initial_data.get(
            'username'
        ):
            raise serializers.ValidationError('Email must be unique.')
        return value

    def validate_username(self, value):
        existing_user = User.objects.filter(username=value).first()
        if existing_user and existing_user.email != self.initial_data.get(
            'email'
        ):
            raise serializers.ValidationError('Username must be unique.')
        if not re.match(r'^[\w.@+-]+$', value) or value == 'me':
            raise serializers.ValidationError('Username is invalid.')
        return value

