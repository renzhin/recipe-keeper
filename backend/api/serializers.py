import base64

import webcolors
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from recipes.models import (
    Follow,
    Tag,
    Measurement,
    Recipe,
    Ingredient,
    IngredientRecipe,
    Favourite,
    Shoplist,
)
from recipes.validators import validate_me, username_validator

User = get_user_model()


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')
            # И извлечь расширение файла.
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=254,
        required=True,
    )
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[validate_me, username_validator]
    )
    first_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    password = serializers.CharField(
        max_length=150,
        required=True,
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        ]
        # extra_kwargs = {'password': {'write_only': True}} Полезный приём

    def create(self, validated_data):
        # Проверка уникальности email и username перед созданием пользователя
        email = validated_data.get('email')
        username = validated_data.get('username')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': '"Этот email занят".'}
            )
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {'username': '"Этот username занят".'}
            )

        # Хеширование пароля и создание пользователя
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)


class CurrentUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        return False


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField(
        source='measurement_unit.type'
    )

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient_id.id')
    name = serializers.CharField(source='ingredient_id.name')
    measurement_unit = serializers.CharField(
        source='ingredient_id.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']


class MeasurementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Measurement
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class FavouriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favourite
        fields = '__all__'


class ShoplistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shoplist
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True
    )
    ingredients = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(), required=True
        ), required=True
    )
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)

        for tag in tags_data:
            recipe.tags.add(tag)

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id']
            amount = ingredient_data['amount']
            ingredient = Ingredient.objects.get(id=ingredient_id)
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)

        instance.tags.clear()
        for tag in tags_data:
            instance.tags.add(tag)

        instance.ingredientrecipe_set.all().delete()
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id']
            amount = ingredient_data['amount']
            ingredient = Ingredient.objects.get(id=ingredient_id)
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=amount
            )

        instance.save()
        return instance

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favourite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Shoplist.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False


# class RecipeSerializer(serializers.ModelSerializer):
#     tags = TagSerializer(many=True, source='tag')
#     author = UserSerializer()
#     ingredients = IngredientRecipeSerializer(
#         many=True,
#         source='ingredientrecipe_set'
#     )
#     is_favorited = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField()
#     image = Base64ImageField(required=False, allow_null=True)

#     class Meta:
#         model = Recipe
#         fields = [
#             'id', 'tags', 'author', 'ingredients', 'is_favorited',
#             'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
#         ]

#     def get_is_favorited(self, obj):
#         request = self.context.get('request')
#         if request and request.user.is_authenticated:
#             return Favourite.objects.filter(
#                 user=request.user, recipe=obj
#             ).exists()
#         return False

#     def get_is_in_shopping_cart(self, obj):
#         request = self.context.get('request')
#         if request and request.user.is_authenticated:
#             return Shoplist.objects.filter(
#                 user=request.user, recipe=obj
#             ).exists()
#         return False
