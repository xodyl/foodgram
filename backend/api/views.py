from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend

from api.models import Tag, Ingredient, Recipe
from api.serializers import (
    TagSerializer, IngredientSerializer, 
    RecipeSerializer, RecipeCreateSerializer
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None  


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None  
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('author', 'tags')
    
    def get_permissions(self):
        if self.action in ('create', 'patch', 'delete'):
            return (permissions.IsAuthenticated(),)
        return (permissions.AllowAny(),)

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        
        if is_favorited is not None:
            queryset = queryset.filter(favorited_by=self.request.user)
        
        if is_in_shopping_cart is not None:
            queryset = queryset.filter(in_shopping_cart=self.request.user)
        
        return queryset

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)

