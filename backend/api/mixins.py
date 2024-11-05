from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets

from api.models import RecipeIngredient


class IngridientTagMixin(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (permissions.AllowAny, )


class AmountMixin():
    def update_or_create_ingredient(self, recipe, ingredients) -> None:
        recipe.ingredients.clear()
        ingredient_list = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredient_list)


class ChosenMixin():
    def get_chosen_recipe(self, obj, model) -> bool:
        user = self.context['request'].user
        return (
            False if user.is_anonymous
            else model.objects.filter(user=user, recipe=obj).exists()
        )
