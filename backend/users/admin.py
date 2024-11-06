from django.contrib import admin
from django.contrib.auth import get_user_model

from api.models import Recipe


User = get_user_model()


class RecipeInline(admin.StackedInline):
    model = Recipe
    extra = 0


@admin.register(User)
class User(admin.ModelAdmin):
    inlines = (RecipeInline,)
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'email',
        'avatar'
    )
    search_fields = ('user', 'email',)
    list_filter = ('role',)
