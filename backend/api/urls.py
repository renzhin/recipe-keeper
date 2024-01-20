from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RecipeViewSet, FollowViewSet, IngredientViewSet


app_name = 'api'


v1_router = DefaultRouter()

v1_router.register(r'users', UserViewSet)
v1_router.register(r'recipes', RecipeViewSet)
v1_router.register(r'follows', FollowViewSet)
v1_router.register(r'ingredients', IngredientViewSet)

urlpatterns = [path('', include(v1_router.urls))]
