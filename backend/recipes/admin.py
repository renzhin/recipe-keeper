from django.contrib import admin
from django.db.models import Count
from django.contrib.auth.models import Group

from users.models import ModifiedUser
from .models import (
    Follow,
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

    def total_favorites(self, obj):
        return obj.favors_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(favors_count=Count('favors'))
        return queryset

    total_favorites.short_description = 'В избранном'
    total_favorites.admin_order_field = 'favors_count'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('name', 'measurement_unit',)


class ModifiedUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email'
    )
    list_filter = ('first_name', 'email',)


admin.site.register(Follow)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Measurement)
admin.site.register(Tag)
admin.site.register(Favourite)
admin.site.register(Shoplist)
admin.site.register(ModifiedUser, ModifiedUserAdmin)
