from djoser.views import UserViewSet as BaseUserViewSet
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import permissions, views, viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action

from users.serializers import (
    SignUpSerializer,
    AvatarSerializer,
    UserProfileSerializer,
    SetPasswordSerializer,
) 


User = get_user_model()


class UsersViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SignUpSerializer
        if self.request.method == 'GET':
            return UserProfileSerializer

    @action(
        ['PUT', 'DELETE'], 
        detail=False, 
        url_path='me/avatar', 
        serializer_class=AvatarSerializer, 
        permission_classes=(permissions.IsAuthenticated,)
    )
    def upload_avatar(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=self.request.user.id)
        if request.method == 'PUT':
            serializer = AvatarSerializer(
                instance=user, 
                data=request.data, 
                partial=True, 
                context={'request':request}
            )
            if 'avatar' not in self.request.data:
                return Response(
                        status=status.HTTP_400_BAD_REQUEST
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            avatar = user.avatar
            avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['GET'],
        detail=False,
        url_name='current_user',
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def me(self, request):
        serializer = UserProfileSerializer(
            request.user,
            context={'request': request}
        )
        return Response(data=serializer.data)
 
    @action(
        ['POST'],
        detail=False,
        url_name='set_new_password',
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(
            instance=self.request.user,
            validated_data=serializer.validated_data
        )
        return Response(
            'Пароль успешно изменен',
            status=status.HTTP_200_OK
        )
