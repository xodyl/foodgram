from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.constants import API_VERSION
from api.views import SignUpView, TokenView, UserProfileView, UsersViewSet


app_name = 'api'

router = SimpleRouter()

router.register(r'users', UsersViewSet, basename='users')

urlpatterns = [
    path(API_VERSION + 'users/', SignUpView.as_view(), name='signup'),
    path(API_VERSION + 'auth/token/', TokenView.as_view(), name='token'),
    path(
        API_VERSION + 'users/me/',
        UserProfileView.as_view(),
        name='user_profile'
    ),
    path(API_VERSION, include(router.urls)),
]
