from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView,
    CustomLogoutView,
    PasswordReset,
    CurrentUserView
)
from .views import UserViewSet, RecipeViewSet, FollowViewSet, IngredientViewSet

app_name = 'api'


v1_router = DefaultRouter()

v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'follows', FollowViewSet, basename='follows')
v1_router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path(
        'auth/token/login/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
        ),
    path('auth/token/logout/',
         CustomLogoutView.as_view(),
         name='logout'),
    path(
        'users/set_password/',
        PasswordReset.as_view({'post': 'set_password'}),
        name='set_password'
    ),
    path(
        'users/me/',
        CurrentUserView.as_view(),
        name='current_user'
    ),
    path('', include(v1_router.urls)),
]
