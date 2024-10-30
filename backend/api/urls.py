from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.constants import API_VERSION
from users.views import UsersViewSet, TagViewSet


app_name = 'api'

router = SimpleRouter()

router.register(r'users', UsersViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    path(API_VERSION, include(router.urls)),
    path(API_VERSION, include('djoser.urls')),
    path(API_VERSION + 'auth/', include('djoser.urls.authtoken')),
]

