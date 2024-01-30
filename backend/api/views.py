from rest_framework import viewsets, generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny
)
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Exists
from djoser.views import TokenCreateView, TokenDestroyView
from djoser.views import UserViewSet as DjoserUserViewSet

from api.pagination import CustomPagination
from .serializers import (
    UserSerializer,
    FollowSerializer,
    FollowCreateSerializer,
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
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('user__username', 'following__username')

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserFollowView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, id):
        user_to_subscribe = get_object_or_404(User, id=id)
        user = request.user

        # Проверяем, что пользователь не пытается подписаться на самого себя
        if user == user_to_subscribe:
            return Response(
                {'error': 'Вы не можете подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, существует ли уже запись подписки между пользователями
        if Follow.objects.filter(
            follower=user,
            following=user_to_subscribe
        ).exists():
            return Response(
                {'error': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаем запись подписки
        _, created = Follow.objects.get_or_create(
            follower=user,
            following=user_to_subscribe
        )

        # перенаправляем на сериалайзер, чтобы получить ответ как в ReDoc
        serializer = FollowCreateSerializer(user_to_subscribe)
        return Response(serializer.data)

    def delete(self, request, id):
        # Получаем пользователя, от которого нужно отписаться
        user_to_unsubscribe = get_object_or_404(User, id=id)
        # Получаем текущего пользователя, который хочет отписаться
        user = request.user

        # Удаляем запись подписки
        Follow.objects.filter(
            follower=user,
            following=user_to_unsubscribe
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вью для создания рецепта с готовыми энгридиентами."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('tags', 'author',)
    filterset_fields = ('tags__slug', 'author',)  # не работает по тегам, slug?

    def get_serializer_class(self):
        # перекидываем все гет запросы на сериалайзер RecipeGetSerializer
        if self.action == 'list':
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user

        queryset = super().get_queryset()
        if user.is_authenticated:
            # вытаскиваем параметры из запроса
            tags_slugs = self.request.query_params.getlist('tags')

            if tags_slugs:
                # фильтруем рецепты по переданным слагам тегов
                queryset = queryset.filter(tags__slug__in=tags_slugs)

            # анотируем запрос в "избранном" и "шоплисте"
            queryset = queryset.annotate(
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

        return queryset


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
