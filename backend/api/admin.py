from django import forms
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.contrib import admin, auth
from rest_framework.authtoken.models import TokenProxy

from api.models import RecipeIngredient, Ingredient, Recipe, Tag
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
)


class TagAdminForm(forms.ModelForm):

    class Meta:
        model = Tag
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        serializer = TagSerializer(data={
            'name': cleaned_data.get('name'),
            'slug': cleaned_data.get('slug'),
        })
        try:
            serializer.is_valid(raise_exception=True)
        except DRFValidationError as e:
            raise forms.ValidationError(e.detail)
        return cleaned_data


class IngredientAdminForm(forms.ModelForm):

    class Meta:
        model = Ingredient
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        serializer = IngredientSerializer(data={
            'name': cleaned_data.get('name'),
            'measurement_unit': cleaned_data.get('measurement_unit'),
        })
        try:
            serializer.is_valid(raise_exception=True)
        except DRFValidationError as e:
            raise forms.ValidationError(e.detail)
        return cleaned_data


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ('ingredient',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    forms = TagAdminForm
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('slug',)
    list_filter = ('slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    forms = IngredientAdminForm
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('measurement_unit',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'cooking_time',
        'in_favorite_amount',
        'pub_date'
    )
    list_filter = ('tags', 'pub_date',)
    list_editable = ('name', 'cooking_time',)
    filter_horizontal = ('tags',)
    search_fields = ('name', 'author__username', 'ingredients__name')
    inlines = (RecipeIngredientInline,)
    fields = ('image',
              ('name', 'author'),
              'text',
              ('tags', 'cooking_time'))

    def in_favorite_amount(self, obj):
        return obj.recipe.count()

    in_favorite_amount.short_description = 'В избранном'


admin.site.empty_value_display = 'Не задано'
admin.site.unregister(auth.models.Group)
admin.site.unregister(TokenProxy)
