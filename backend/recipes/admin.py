from django.contrib import admin
from django.db.models import Count
from django.contrib.auth.models import Group

from .models import (
    Recipe,
    Ingredient,
    Measurement,
    Tag,
    TagRecipe,
    IngredientRecipe,
    Favourite,
    Shoplist
)

admin.site.unregister(Group)  # убираем раздел с группами и пользователями


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class FavouriteInline(admin.TabularInline):
    model = Favourite
    extra = 0
    readonly_fields = ['user']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [TagRecipeInline, IngredientRecipeInline, FavouriteInline]
    list_display = (
        'name',
        'author',
        'total_favorites',
    )
    list_filter = ('tags', 'author', 'name',)
    search_fields = ('name',)

    def total_favorites(self, obj):
        return obj.favors_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(favors_count=Count('favors'))
        return queryset

    total_favorites.short_description = 'В избранном'
    total_favorites.admin_order_field = 'favors_count'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('type',)
    search_fields = ('type',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('measurement_unit',)
    search_fields = ('name',)


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


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favourite, FavouriteAdmin)
admin.site.register(Shoplist, ShoplistAdmin)
