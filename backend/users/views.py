from djoser.views import UserViewSet as BaseUserViewSet
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import permissions, views, viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action

from api.models import Subscription
from api.pagination import LimitPagination
from users.serializers import (
    SignUpSerializer,
    AvatarSerializer,
    UserProfileSerializer,
    SetPasswordSerializer,
    SubscribeSerializer,
) 


User = get_user_model()


class UsersViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPagination
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
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        ['POST', 'DELETE'],
        detail=True,
        url_name='subscribe',
        permission_classes=(permissions.IsAuthenticated, )
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        user = self.request.user
        is_subscription_exist = user.subscriptions.filter(
            author=author
        ).exists()
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data=request.data,
                context={
                    'user': user,
                    'author': author,
                    'request': request,
                    'is_subscription_exist': is_subscription_exist}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if is_subscription_exist:
            user.subscriptions.get(author=author).delete()
            return Response(
                'Успешная отписка',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'errors': 'Вы не подписаны'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        ['GET'],
        detail=False,
        url_name='get_subscriptions',
        permission_classes=(permissions.IsAuthenticated, ),
    )
    def subscriptions(self, request):
        paginate_subs = self.paginate_queryset(
            Subscription.objects.filter(user=self.request.user)
        )
        serializer = SubscribeSerializer(
            paginate_subs,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
