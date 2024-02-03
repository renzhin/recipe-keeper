from rest_framework.permissions import BasePermission


class IsRecipeAuthorOrReadOnly(BasePermission):
    """Проверяет, является ли пользователь автором рецепта."""

    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD, OPTIONS запросы любому пользователю.
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Разрешаем только автору рецепта изменять или удалять его.
        return obj.author == request.user
