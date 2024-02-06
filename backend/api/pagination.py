from rest_framework.pagination import (
    LimitOffsetPagination
)


class CustomPagination(LimitOffsetPagination):
    default_limit = 6  # Стандартный лимит по умолчанию
    max_limit = 1000  # Максимальный лимит страницы
