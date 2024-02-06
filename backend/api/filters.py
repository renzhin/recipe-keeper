from django_filters.rest_framework import filters, FilterSet

from recipes.models import Recipe, Tag, Ingredient


class IngredientFilter(FilterSet):
    """Фильтр по имени для ингредиентов"""
    name = filters.CharFilter(
        field_name='name',
        # Ищем значения, начинающиеся с указанной строки, игнорируя регистр
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтры для модели Recipe."""
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, queryset, name, value):
        # Фильтруем рецепты, добавленные в избранное пользователем
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(
                favors__user=user
            )
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        # Фильтруем рецепты, добавленные в шоплист пользователем
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(
                shops__user=user
            )
        return queryset
