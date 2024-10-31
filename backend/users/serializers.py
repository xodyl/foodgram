import base64
import re

from rest_framework import serializers
from djoser.serializers import UserSerializer as BaseUserSerializer
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from api.constants import USERNAME_LENGTH
from users.constants import EMAIL_FIELD_LENGTH


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 
                  'last_name', 'is_subscribed', 'avatar')
        read_only_filds = ('id',)

    def validate(self, attrs):
        if self.context['request'].method == 'PATCH':
            username = attrs.get('username')
            first_name = attrs.get('first_name')
            last_name = attrs.get('last_name')

            # if first_name == '' or last_name == '':
            #     raise serializers.ValidationError(
            #         r'First and last name should not be empty.'
            #     )
            # if username is not None and not re.match(r'^[\w.@+-]+$', username):
            #     raise serializers.ValidationError(
            #         r'Username must match the pattern: ^[\w.@+-]+\Z'
            #     )
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
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')

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

