from django.core.validators import RegexValidator
from rest_framework import serializers


def validate_me(value):
    if value == 'me':
        raise serializers.ValidationError('Имя пользователя "me" запрещено.')


def validate_cooking_time(cooking_time):
    if cooking_time < 1:
        raise serializers.ValidationError(
            'Время приготовления не должно быть меньше минуты')
    return cooking_time


username_validator = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message='Буквы, цифры и символы @/./+/-/_',
)
