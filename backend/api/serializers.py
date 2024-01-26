import base64

import webcolors
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from recipes.models import (
    Follow,
    Tag,
    TagRecipe,
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


# class CreateRecipeSerializer(serializers.ModelSerializer):
#     tags = serializers.PrimaryKeyRelatedField(
#         many=True, queryset=Tag.objects.all(), required=True,
#     )
#     ingredients = serializers.PrimaryKeyRelatedField(
#         many=True,
#         queryset=Ingredient.objects.all(), required=True
#     )
#     image = serializers.ImageField(required=False, allow_null=True)
#     is_favorited = serializers.BooleanField(
#         default=False,
#         read_only=True,
#         )
#     is_in_shopping_cart = serializers.BooleanField(
#         default=False,
#         read_only=True,
#     )

#     class Meta:
#         model = Recipe
#         fields = [
#             'id', 'tags', 'ingredients', 'is_favorited',
#             'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
#         ]

#     def create(self, validated_data):
#         ingredients_data = validated_data.pop('ingredients')

#         recipe = Recipe.objects.create(**validated_data)

#         tags_data = validated_data.pop('tags')
#         for tag in tags_data:
#             TagRecipe.objects.create(tag=tag, recipe=recipe)

#         for ingredient in ingredients_data:
#             # Сохраняем ингредиенты
#             IngredientRecipe.objects.create(recipe=recipe, ingredient_id=ingredient)

#         return recipe


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.BooleanField(
        default=False,
        read_only=True
        )
    is_in_shopping_cart = serializers.BooleanField(
        default=False,
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]

    def get_ingredients(self, obj):
        # Получаем все связанные объекты IngredientRecipe для данного рецепта
        ingredients_recipes = IngredientRecipe.objects.filter(recipe_id=obj.id)

        # Сериализуем каждый объект IngredientRecipe и добавляем поле amount
        serialized_data = []
        for ingredient_recipe in ingredients_recipes:
            ingredient_data = IngredientSerializer(ingredient_recipe.ingredient_id).data
            ingredient_data['amount'] = ingredient_recipe.amount
            serialized_data.append(ingredient_data)

        return serialized_data


    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)

        tags_data = validated_data.pop('tags')
        for tag in tags_data:
            TagRecipe.objects.create(tag=tag, recipe=recipe)

        for ingredient in ingredients_data:
            # Сохраняем ингредиенты
            IngredientRecipe.objects.create(recipe=recipe, ingredient_id=ingredient)

        return recipe
