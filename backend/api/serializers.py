import re
import secrets
import string
import base64

from django.conf import settings
from django.core.mail import send_mail
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from api.constants import USERNAME_LENGTH
from users.constants import CONFIRMATION_CODE_LENGTH, EMAIL_FIELD_LENGTH


def generate_confirmation_code(length=CONFIRMATION_CODE_LENGTH):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_confirmation_email(email, confirmation_code):
    send_mail(subject='Confirmation Code',
              message=f'Your confirmation code is: {confirmation_code}',
              from_email=settings.EMAIL_HOST_USER,
              recipient_list=[email])


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password']
        self.fields['username'] = serializers.CharField()
        self.fields['confirmation_code'] = serializers.CharField(
            max_length=CONFIRMATION_CODE_LENGTH,
            required=True
        )

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if confirmation_code != user.confirmation_code:
            raise ValidationError('Incorrect confirmation code')
        return attrs


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=EMAIL_FIELD_LENGTH,
                                   required=True)
    username = serializers.CharField(max_length=USERNAME_LENGTH,
                                     required=True)

    class Meta:
        model = User
        fields = ('email', 'username')

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

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')
        confirmation_code = generate_confirmation_code()
        user, created = User.objects.get_or_create(
            email=email,
            username=username,
            defaults={'confirmation_code': confirmation_code},
        )
        send_confirmation_email(email, confirmation_code)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=EMAIL_FIELD_LENGTH,
        required=True
    )
    username = serializers.CharField(
        max_length=USERNAME_LENGTH,
        required=True
    )
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

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


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

