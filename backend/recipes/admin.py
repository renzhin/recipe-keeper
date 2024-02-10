from django.contrib import admin
from django.db.models import Count
from django.contrib.auth.models import Group

from .models import (
    Recipe,
    Ingredient,
    Measurement,
    Tag,
    IngredientRecipe,
    Favourite,
    Shoplist
)

admin.site.unregister(Group)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientRecipeInline]
    list_display = (
        'name',
        'author',
        'total_favorites',
    )
    list_filter = ('tags', 'author', 'name',)
    search_fields = ('name',)

    def total_favorites(self, obj):
        return obj.favourite_recipes_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            favourite_recipes_count=Count('favourite_recipes')
        )
        return queryset

    total_favorites.short_description = 'В избранном'
    total_favorites.admin_order_field = 'favourite_recipes_count'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('t_name',)
    search_fields = ('t_name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('measurement_unit',)
    search_fields = ('name',)


@admin.register(Shoplist)
class ShoplistAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user',)
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'recipe__name',
    )


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user',)
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'recipe__name',
    )
