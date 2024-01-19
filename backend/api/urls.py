from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RecipeViewSet, FollowViewSet


app_name = 'api'


v1_router = DefaultRouter()

v1_router.register(r'users', UserViewSet)
v1_router.register(r'recipes', RecipeViewSet)
v1_router.register(r'follows', FollowViewSet)

urlpatterns = [path('v1/', include(v1_router.urls))]
