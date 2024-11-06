from django.contrib import admin, auth
from rest_framework.authtoken.models import TokenProxy

from api.models import RecipeIngredient, Ingredient, Recipe, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('slug',)
    list_filter = ('slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
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

    def in_favorite_amount(self, obj):
        return obj.recipe.all().count()

    in_favorite_amount.short_description = 'В избранном'


admin.site.empty_value_display = 'Не задано'
admin.site.unregister(auth.models.Group)
admin.site.unregister(TokenProxy)
