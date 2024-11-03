import base64
import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from api.constants import USERNAME_LENGTH
from api.models import Subscription, Recipe
from users.constants import EMAIL_FIELD_LENGTH


User = get_user_model()


class RecipeMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


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


class SignUpSerializer(BaseUserCreateSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(
        required=True,
        max_length=USERNAME_LENGTH
    )
    last_name = serializers.CharField(
        required=True,
        max_length=USERNAME_LENGTH
    )
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
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )

    def validate_first_name(self, value):
        return self._validate_name_length(value)

    def validate_last_name(self, value):
        return self._validate_name_length(value)

    def _validate_name_length(self, value):
        if len(value) > USERNAME_LENGTH:
            raise serializers.ValidationError(
                'Имя не может содержать более 50 символов.'
            )
        return value

    def validate_email(self, value):
        existing_user = User.objects.filter(email=value).first()
        if existing_user and existing_user.email == self.initial_data.get(
            'email'
        ):
            raise serializers.ValidationError(
                'Почтовый адрес уже зарегистрирован!'
            )
        return value

    def validate_username(self, value):
        existing_user = User.objects.filter(username=value).first()
        if existing_user and existing_user.username == self.initial_data.get(
            'username'
        ):
            raise serializers.ValidationError('Логин уже занят!')
        if not re.match(r'^[\w.@+-]+$', value) or value == 'me':
            raise serializers.ValidationError('Невалидный логин')
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user or user.is_anonymous:
            return False
        if user == obj:
            return False
        return user.subscriptions.filter(author=obj).exists()


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    class Meta:
        model = User
        write_only = ('new_password', 'current_password')

    def validate(self, data):
        if not self.context['request'].user.check_password(
            data.get('current_password')
        ):
            raise ValidationError(
                {'current_password': 'Неправильный пароль'}
            )
        if data.get('current_password') == data.get('new_password'):
            raise ValidationError(
                {'new_password': 'Новый пароль совпадает с предыдущим!'}
            )
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class SubscribeSerializer(serializers.ModelSerializer):

    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeMiniSerializer(
        read_only=True,
        many=True,
        source='author.recipe'
    )
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(
        source='author.avatar',
        required=False,
        allow_null=True
    )

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def validate(self, data):
        if self.context['user'] == self.context['author']:
            raise ValidationError('Нельзя подписываться на себя!')
        if self.context['is_subscription_exist']:
            raise ValidationError('Нельзя подписаться дважды!')
        return data

    def get_is_subscribed(self, obj):
        if not obj.user:
            return False
        return obj.user.subscriptions.filter(author=obj.author).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        if recipes_limit:
            representation['recipes'] = representation[
                'recipes'
            ][:int(recipes_limit)]
        return representation

    def get_recipes_count(self, obj):
        return obj.author.recipe.count()
