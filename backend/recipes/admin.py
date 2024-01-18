from django.contrib import admin
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


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [TagRecipeInline, IngredientRecipeInline]


admin.site.register(Follow)
admin.site.register(Ingredient)
admin.site.register(Measurement)
admin.site.register(Tag)
admin.site.register(Favourite)
admin.site.register(Shoplist)
