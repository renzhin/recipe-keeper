from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ModifiedUser, Follow


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'follower',
        'following'
    )
    list_filter = ('follower', 'following',)
    search_fields = (
        'follower__first_name',
        'follower__last_name',
        'follower__first_name',
        'follower__last_name',
    )


@admin.register(ModifiedUser)
class ModifiedUserAdmin(UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'get_followers_count',
        'get_recipe_count'
    )
    list_filter = ('first_name', 'email',)
    search_fields = (
        'first_name',
        'last_name',
        'email',
    )

    def get_followers_count(self, obj):
        return obj.followers.count()
    get_followers_count.short_description = 'Подписчики'

    def get_recipe_count(self, obj):
        return obj.recipes.count()
    get_recipe_count.short_description = 'Количество рецептов'
