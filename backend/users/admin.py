from django.contrib import admin

from .models import ModifiedUser, Follow


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


class ModifiedUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email'
    )
    list_filter = ('first_name', 'email',)
    search_fields = (
        'first_name',
        'last_name',
        'email',
    )


admin.site.register(Follow, FollowAdmin)
admin.site.register(ModifiedUser, ModifiedUserAdmin)
