from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView,
    CustomLogoutView,
    PasswordReset,
    CurrentUserView,
    AddInFavoritesView,
    AddInShoplistView,
)
from .views import (
    UserViewSet,
    RecipeViewSet,
    IngredientViewSet,
    TagViewSet,
    )

app_name = 'api'


v1_router = DefaultRouter()

v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'ingredients', IngredientViewSet, basename='ingredients')
v1_router.register(r'tags', TagViewSet, basename='tags')

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
    path(
        'recipes/<int:pk>/favorite/',
        AddInFavoritesView.as_view(),
        name='add_in_favorites'
        ),
    path(
        'recipes/<int:pk>/shopping_cart/',
        AddInShoplistView.as_view(),
        name='add_in_favorites'
        ),
    path('', include(v1_router.urls)),  # не забыть про очередность
]
