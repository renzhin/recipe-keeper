from rest_framework import (
    viewsets,
    filters,
    status
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from django.http import HttpResponse
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Exists
from djoser.views import UserViewSet as DjoserUserViewSet

from api.filters import (
    RecipeFilter,
    IngredientFilter
)
from api.pagination import CustomPagination
from api.permissions import IsRecipeAuthorOrReadOnly
from .serializers import (
    UserSerializer,
    FollowSerializer,
    FollowCreateListSerializer,
    RecipeSerializer,
    RecipeGetSerializer,
    IngredientSerializer,
    TagSerializer,
    CurrentUserSerializer,
    FavouriteShoplistRecipeSerializer
)
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favourite,
    Shoplist
)
from users.models import (
    Follow,
)

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для пользователей, подписок и me"""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    @action(
            detail=False,
            methods=['get'],
            url_path='me',
            permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = CurrentUserSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
            detail=False,
            methods=['get'],
            url_path='subscriptions',
            permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        # Получаем список всех пользователей, на которых подписан текущий
        subscriptions = User.objects.filter(followers__follower=request.user)
        # Применяем кастомную пагинацию
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(subscriptions, request)
        serializer = FollowCreateListSerializer(
            result_page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
            detail=True, methods=['post', 'delete'],
            url_path='subscribe',
            permission_classes=[IsAuthenticatedOrReadOnly]
    )
    def subscribe(self, request, id):
        user_to_subscribe = get_object_or_404(User, id=id)
        user = request.user

        if request.method == 'POST':
            # Проверяем, что пользователь не пытается подписаться на себя
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
            serializer = FollowCreateListSerializer(
                user_to_subscribe, context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            # Проверяем, существует ли запись подписки между пользователями
            follow_inst = Follow.objects.filter(
                follower=user,
                following=user_to_subscribe
            ).first()
            if not follow_inst:
                return Response(
                    {'error': 'Подписка не существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Удаляем запись подписки
            follow_inst.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(viewsets.ModelViewSet):
    """Вьюсет для подписсок."""
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('user__username', 'following__username')

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для создания и редактирования
    рецепта с готовыми ингредиентами +
    избранное и шоплист.
    """

    permission_classes = [IsAuthenticatedOrReadOnly, IsRecipeAuthorOrReadOnly]
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

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

    def pre_favorite_shoplist(
            self,
            request,
            favorite_shoplist,
            name,
            **kwargs
    ):
        user = self.request.user
        if request.method == 'POST':
            try:
                # Попытка получить объект рецепта по id
                recipe = Recipe.objects.get(id=kwargs['pk'])
            except Recipe.DoesNotExist:
                return Response(
                    {'detail': 'Рецепт не существует.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if favorite_shoplist.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                return Response(
                    {"message": "Рецепт уже добавлен в {name}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite_shoplist.objects.create(user=user, recipe=recipe)
            serializer = FavouriteShoplistRecipeSerializer(
                recipe,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=kwargs['pk'])
            try:
                favorite_shoplist.objects.get(
                    user=user, recipe=recipe
                ).delete()
                return Response(
                    {'detail': f'Рецепт удален из {name}.'},
                    status=status.HTTP_204_NO_CONTENT
                )
            except favorite_shoplist.DoesNotExist:
                return Response(
                    {'detail': f'Рецепт не был ранее добавлен в {name}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
            detail=True,
            url_path='favorite',
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, **kwargs):
        return self.pre_favorite_shoplist(
            request,
            Favourite,
            'избранное',
            **kwargs
        )

    @action(
            detail=True,
            url_path='shopping_cart',
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, **kwargs):
        return self.pre_favorite_shoplist(
            request,
            Shoplist,
            'шоплист',
            **kwargs
        )

    @action(
            detail=False,
            methods=['get'],
            url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        # Получаем ингредиенты для рецептов в списке покупок текущего юзера
        user_shoplist = Shoplist.objects.filter(
            user=request.user
        ).values_list(
            'recipe__ingredient_recipes__ingredient__name',
            'recipe__ingredient_recipes__ingredient__measurement_unit__type',
        ).annotate(
            total_amount=Sum('recipe__ingredient_recipes__amount')
        )

        # Формируем текст списка покупок
        shopping_list = ['Список покупок:\n']
        for ingredient in user_shoplist:
            name = ingredient[0]
            unit = ingredient[1]
            amount = ingredient[2]
            shopping_list.append(f'\n{name} - {amount}, {unit}')

        # Создаем HTTP-ответ с содержимым списка покупок
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shoplst.txt"'
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет списка ингредиентов для эндпоина ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    pagination_class = None
    filterset_fields = ('name',)
    search_fields = ('name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет списка тегов для эндпоина тегов."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None
