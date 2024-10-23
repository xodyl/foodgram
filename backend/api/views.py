from django.shortcuts import get_object_or_404
from rest_framework import permissions, views, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api import serializers
from api.permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
)
from users.models import User


class SignUpView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = serializers.SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TokenView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = serializers.CustomTokenObtainPairSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        access = AccessToken.for_user(user)
        user.confirmation_code = None
        user.save()
        return Response({'token': str(access)})


class UserProfileView(views.APIView):

    def get_user(self):
        return self.request.user

    def get(self, request, format=None):
        serializer = serializers.UserProfileSerializer(self.get_user())
        return Response(serializer.data)

    def patch(self, request, format=None):
        instance = self.get_user()
        serializer = serializers.UserProfileSerializer(
            instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UsersSerializer
    permission_classes = (IsAdmin, )
    filter_backends = (SearchFilter,)
    search_fields = ('username', )
    lookup_field = 'username'

