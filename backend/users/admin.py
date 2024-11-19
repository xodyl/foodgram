from django import forms
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.contrib import admin
from django.contrib.auth import get_user_model

from api.models import Recipe
from users.serializers import SignUpSerializer


User = get_user_model()


class UserAdminForm(forms.ModelForm):

    class Meta:
        model = User
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        serializer = SignUpSerializer(data={
            'email': cleaned_data.get('email'),
            'username': cleaned_data.get('username'),
            'first_name': cleaned_data.get('first_name'),
            'last_name': cleaned_data.get('last_name'),
            'password': cleaned_data.get('password') or 'dummy_password',
        })
        try:
            serializer.is_valid(raise_exception=True)
        except DRFValidationError as e:
            raise forms.ValidationError(e.detail)

        return cleaned_data


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
