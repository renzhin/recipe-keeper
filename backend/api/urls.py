from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    RecipeViewSet,
    IngredientViewSet,
    TagViewSet,
    FollowViewSet
)

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'ingredients', IngredientViewSet, basename='ingredients')
v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register(r'follow', FollowViewSet, basename='following')


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(v1_router.urls)),
]
