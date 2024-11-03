from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.constants import API_VERSION
from api.views import TagViewSet, IngredientViewSet, RecipeViewSet
from users.views import UsersViewSet


app_name = 'api'


router = SimpleRouter()


router.register(r'users', UsersViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='resipe')


urlpatterns = [
    path(API_VERSION, include(router.urls)),
    path(API_VERSION + 'auth/', include('djoser.urls.authtoken')),
]
