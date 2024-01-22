from django.core.validators import RegexValidator
from rest_framework import serializers


def validate_me(value):
    if value == 'me':
        raise serializers.ValidationError('Имя пользователя "me" запрещено.')


username_validator = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message='Буквы, цифры и символы @/./+/-/_',
)
