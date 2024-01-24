from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from djoser.views import TokenCreateView, TokenDestroyView
from djoser.views import UserViewSet as DjoserUserViewSet

from api.pagination import CustomPagination
from .serializers import (
    UserSerializer,
    FollowSerializer,
    RecipeSerializer,
    IngredientSerializer,
    MeasurementSerializer,
    TagSerializer,
    FavouriteSerializer,
    ShoplistSerializer,
    CurrentUserSerializer,
)
from recipes.models import (
    Follow, Tag, Measurement, Ingredient, Recipe, Favourite, Shoplist
)

User = get_user_model()


class CustomTokenObtainPairView(TokenCreateView):
    permission_classes = [AllowAny]


class CustomLogoutView(TokenDestroyView):
    permission_classes = [IsAuthenticated]


class PasswordReset(DjoserUserViewSet):
    permission_classes = [IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = CustomPagination


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = CurrentUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class MeasurementViewSet(viewsets.ModelViewSet):
    serializer_class = MeasurementSerializer
    queryset = Measurement.objects.all()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class FavouriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavouriteSerializer
    queryset = Favourite.objects.all()


class ShoplistViewSet(viewsets.ModelViewSet):
    serializer_class = ShoplistSerializer
    queryset = Shoplist.objects.all()
