from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from .serializers import (
    UserSerializer,
    FollowSerializer,
    RecipeSerializer,
    IngredientSerializer,
    MeasurementSerializer,
    TagSerializer,
    FavouriteSerializer,
    ShoplistSerializer,
)
from recipes.models import (
    Follow, Tag, Measurement, Ingredient, Recipe, Favourite, Shoplist, User
)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class MeasurementViewSet(viewsets.ModelViewSet):
    serializer_class = MeasurementSerializer
    queryset = Measurement.objects.all()


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class FavouriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavouriteSerializer
    queryset = Favourite.objects.all()


class ShoplistViewSet(viewsets.ModelViewSet):
    serializer_class = ShoplistSerializer
    queryset = Shoplist.objects.all()
