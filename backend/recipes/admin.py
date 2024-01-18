from django.contrib import admin

from .models import (
    Follow, Recipe, Ingredient, Measurement, Tag, Favourite, Shoplist
)

admin.site.register(Follow)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Measurement)
admin.site.register(Tag)
admin.site.register(Favourite)
admin.site.register(Shoplist)
