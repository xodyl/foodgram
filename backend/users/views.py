from djoser.views import UserViewSet as BaseUserViewSet
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import permissions, views, viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action

from users.serializers import (
    SignUpSerializer,
    UserSerializer,
    AvatarSerializer,
) 


User = get_user_model()


class UsersViewSet(BaseUserViewSet):
    filter_backends = (SearchFilter,)
    ordering = ('username', 'id')
    search_fields = ('id', )
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrive'):
            return UserSerializer
        return SignUpSerializer

    @action(detail=False, methods=['put', 'delete'], 
            url_path='me/avatar', serializer_class=AvatarSerializer, 
            permission_classes=(permissions.IsAuthenticated,))
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
        detail=False, methods=('get',),
        url_path='me', serializer_class=UserSerializer,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        obj = get_object_or_404(User, pk=request.user.pk)
        serializer = UserSerializer(obj)
        return Response(serializer.data)
 

# class UserProfileView(views.APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get_user(self):
#         return self.request.user
#
#     def get(self, request, format=None):
#         serializer = UserProfileSerializer(self.get_user())
#         return Response(serializer.data)
#
#     def patch(self, request, format=None):
#         instance = self.get_user()
#         serializer = UserProfileSerializer(
#             instance,
#             data=request.data,
#             partial=True,
#             context={'request': request}
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

