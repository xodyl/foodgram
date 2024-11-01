from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from api.models import Tag, Ingredient, Recipe, RecipeIngredient, Favorite,  ShopingList
from users.serializers import UserProfileSerializer, Base64ImageField
from api.mixins import AmountMixin, ChosenMixin
from api.constants import ( 
    MIN_INGREDIENT_AMOUNT, 
    MAX_INGREDIENT_AMOUNT,
    MIN_INGREDIENT_AMOUNT,
    MAX_INGREDIENT_AMOUNT,
    MIN_COOKING_TIME,
    MAX_COOKING_TIME,
    RECIPE_VALIDATION_MESSAGES,
)


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id',)
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'measurement_unit', 'name')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT,
        max_value=MAX_INGREDIENT_AMOUNT
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer, ChosenMixin):
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    author = UserProfileSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    name = serializers.CharField()
    text = serializers.CharField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        return self.get_chosen_recipe(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_chosen_recipe(obj, ShopingList)


class RecipeSerializer(serializers.ModelSerializer, AmountMixin, ChosenMixin):
    ingredients = AddIngredientSerializer(
        required=True,
        many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
            'author', 'is_favorited', 'is_in_shopping_cart'
        )

    def validate(self, data):
        unique_data: set[int] = set()
        for model in ('ingredients', 'tags'):
            if not data.get(model):
                raise ValidationError(
                    RECIPE_VALIDATION_MESSAGES['EMPTY'][model]
                )
            for obj in data.get(model):
                if isinstance(obj, dict):
                    obj = obj.get('id')
                if obj.id in unique_data:
                    raise ValidationError(
                        RECIPE_VALIDATION_MESSAGES['NOT_UNIQUE'][model]
                    )
                unique_data.add(obj.id)
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.update_or_create_ingredient(
            recipe=recipe, ingredients=ingredients
        )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self.update_or_create_ingredient(
            recipe=instance, ingredients=ingredients
        )
        instance.tags.clear()
        instance.tags.set(tags)
        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def get_is_favorited(self, obj):
        return self.get_chosen_recipe(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_chosen_recipe(obj, ShopingList)


class RecipeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)

