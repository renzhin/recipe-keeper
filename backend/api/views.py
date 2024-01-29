from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import OuterRef, Exists
from djoser.views import TokenCreateView, TokenDestroyView
from djoser.views import UserViewSet as DjoserUserViewSet

from api.pagination import CustomPagination
from .serializers import (
    UserSerializer,
    FollowSerializer,
    RecipeSerializer,
    RecipeGetSerializer,
    IngredientSerializer,
    MeasurementSerializer,
    TagSerializer,
    FavouriteSerializer,
    ShoplistSerializer,
    CurrentUserSerializer,
    FavouriteRecipeSerializer,
    ShoplistRecipeSerializer,
)
from recipes.models import (
    Follow, Tag, Measurement, Ingredient, Recipe, Favourite, Shoplist
)

User = get_user_model()


class CustomTokenObtainPairView(TokenCreateView):
    """Вью для получения токена"""

    permission_classes = [AllowAny]


class CustomLogoutView(TokenDestroyView):
    """Логаут - вью удаления токена"""

    permission_classes = [IsAuthenticated]


class PasswordReset(DjoserUserViewSet):
    """Вью для изменения пароля"""

    permission_classes = [IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    """Вью для получения списка пользователей"""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = CustomPagination


class CurrentUserView(generics.RetrieveAPIView):
    """Вью для эндпоинта me"""

    serializer_class = CurrentUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """Вью для создания рецепта с готовыми энгридиентами."""

    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('tags', 'author',)
    filterset_fields = ('tags', 'author',)  # не работает по тегам, slug?

    def get_serializer_class(self):
        # перекидываем все гет запросы на сериалайзер RecipeGetSerializer
        if self.action == 'list':
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            return Recipe.objects.annotate(
                is_favorited=Exists(
                    Favourite.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                ),
                is_in_shopping_cart=Exists(
                    Shoplist.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                )
            )

        return Recipe.objects.all()


class AddInFavoritesView(APIView):
    """Вью для добавления готового рецепта в избранное."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            # Получаем рецепт
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(
                {"message": "Рецепт не найден"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Получаем пользователя из токена
        user = request.user
        # Проверяем, не добавлен ли уже рецепт в избранное
        if Favourite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"message": "Рецепт уже добавлен в избранное"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Создаем запись об избранном
        favourite = Favourite.objects.create(user=user, recipe=recipe)
        # Создаем сериализатор для ответа
        serializer = FavouriteRecipeSerializer(
            favourite.recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(
        #     {"message": "Рецепт добавлен в избранное"},
        #     status=status.HTTP_201_CREATED
        # )


class AddInShoplistView(APIView):
    """Вью для добавления готового рецепта в шоплист."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            # Получаем рецепт
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(
                {"message": "Рецепт не найден"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Получаем пользователя из токена
        user = request.user
        # Проверяем, не добавлен ли уже рецепт в шоплист
        if Shoplist.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"message": "Рецепт уже добавлен в шоплист"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Создаем запись в шоплисте
        favourite = Shoplist.objects.create(user=user, recipe=recipe)
        # Создаем сериализатор для ответа
        serializer = ShoplistRecipeSerializer(
            favourite.recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вью списка ингредиентов для эндпоина ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # pagination_class = None  # отключение пагинации на уровне вьюсета
    filterset_fields = ('name',)
    search_fields = ('name',)


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
