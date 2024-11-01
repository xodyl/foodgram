from rest_framework import viewsets, filters, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import Http404

from api.models import Tag, Ingredient, Recipe, ShopingList, Favorite
from api.mixins import IngridientTagMixin 
from api.permissions import IsAuthorOrReadOnly
from api.filters import IngredientFilter, TagFilter, RecipeFilter 
from api import serializers
from api.constants import MESSAGES
from api.services import list_to_txt, generate_short_link


class TagViewSet(IngridientTagMixin):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    filterset_class = TagFilter


class IngredientViewSet(IngridientTagMixin):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return serializers.RecipeGetSerializer
        return serializers.RecipeSerializer

    @action(
        ['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated, ),
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(request, ShopingList, pk, 'FAVORITE')
        return self.delete_recipe(request, ShopingList, pk, 'FAVORITE')

    @action(
        ['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated, ),
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_recipe(request, Favorite, pk, 'FAVORITE')
        return self.delete_recipe(request, Favorite, pk, 'FAVORITE')

    def add_recipe(self, request, model, pk, error_key):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        if model.objects.filter(recipe=recipe, user=user).exists():
            return Response(
                MESSAGES['ALREADY_ADDED'][error_key],
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(recipe=recipe, user=user)
        serializer = serializers.RecipeMiniSerializer(recipe)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, request, model, pk, error_key):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        try:
            obj = get_object_or_404(model, recipe=recipe, user=user)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(
                MESSAGES['NOT_FOUND'][error_key],
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        ['GET'],
        detail=False,
        permission_classes=(IsAuthenticated, ),
    )
    def download_shopping_cart(self, request):
        if not request.user.shoping_list.exists():
            return Response(
                'Список покупок пуст.',
                status=status.HTTP_404_NOT_FOUND
            )
        return list_to_txt(user=request.user)

    @action(
        ['GET'],
        detail=True,
        url_path='get-link',
        url_name='get-link',
        permission_classes=(AllowAny, )
    )
    def get_link(self, request, pk):
        short_link = generate_short_link(request, pk)
        return Response({'short-link': short_link})
