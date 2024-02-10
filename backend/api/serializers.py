import base64
import webcolors

from djoser.serializers import UserSerializer as DjoserUserSerializer
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from recipes.models import (
    Tag,
    Recipe,
    Ingredient,
    IngredientRecipe,
    Favourite,
    Shoplist,
)
from users.models import (
    Follow,
)
from recipes.validators import (
    validate_cooking_time
)

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
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializer(DjoserUserSerializer):
    """Сериалайзер для создания пользователя и отдающий список пользователей"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {'email': '"Этот email занят".'}
            )
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                {'username': '"Этот username занят".'}
            )
        return value

    def create(self, validated_data):
        """Хеширование пароля и создание пользователя"""
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated and Follow.objects.filter(
                follower=request.user,
                following=obj
            ).exists()
        )


class CurrentUserSerializer(serializers.ModelSerializer):
    """Сериалайзер для информации о конкеретном пользователе"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

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
        request = self.context.get('request')
        return (
            request.user.is_authenticated and Follow.objects.filter(
                follower=request.user,
                following=obj
            ).exists()
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериалайзер, работающий с подписками"""

    class Meta:
        model = Follow
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер, отдающий ингредиенты"""
    measurement_unit = serializers.StringRelatedField()

    class Meta:
        model = Ingredient
        exclude = ['created_at']


class IngredientSubSerializer(serializers.ModelSerializer):
    """Вложенный сериалайзер рецепта, отдающий ингредиенты с количеством"""
    measurement_unit = serializers.StringRelatedField(
        source='measurement_unit.t_name'
    )
    amount = serializers.SerializerMethodField()
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit', 'amount']

    def get_amount(self, obj):
        ingredient_recipe = obj.ingredient_recipes.first()
        if ingredient_recipe:
            return ingredient_recipe.amount
        return None


class IngredientInsertSerializer(serializers.ModelSerializer):
    """Вложенный сериалайзер создания рецепта для ингредиентов."""
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'amount']


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тегов измерения."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        exclude = ['created_at']


class FavouriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для изранных рецептов пользователя."""

    class Meta:
        model = Favourite
        fields = '__all__'


class ShoplistSerializer(serializers.ModelSerializer):
    """Сериалайзер для рецептов шоплиста пользователя."""

    class Meta:
        model = Shoplist
        fields = '__all__'


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериалайзер для получения информации о рецептах."""
    tags = TagSerializer(many=True, required=False)
    author = UserSerializer()
    ingredients = IngredientSubSerializer(many=True, required=False)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        request = self.context['request']
        return (
            request.user.is_authenticated and Favourite.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        return (
            request.user.is_authenticated and Shoplist.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        )

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания рецепта с переопределением."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientInsertSerializer(
        many=True,
        required=True
    )
    image = Base64ImageField(required=True, allow_null=True)
    cooking_time = serializers.IntegerField(
        validators=[validate_cooking_time]
    )

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        ]

    def validate_tags(self, value):
        # Проверяем, чтобы не было попытки добавить два одинаковых тега
        uniq_tags = set(value)
        if len(value) == 0:
            raise serializers.ValidationError({
                'tags': 'Попытка передать пустой список тегов.'
            })
        elif len(value) != len(uniq_tags):
            raise serializers.ValidationError({
                'tags': 'Попытка добавить два или более идентичных тега.'
            })
        # Проверяем, что переданные теги существуют в базе
        for tag in value:
            if not Tag.objects.filter(pk=tag.pk).exists():
                raise serializers.ValidationError({
                    'tags': 'Тэг отсутствует в базе данных.'
                })
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError({
                'ingredients': 'Нет ни одного ингредиента'
            })
        ingredients = [item['id'] for item in value]
        uniq_ingredients = set(ingredients)

        if len(uniq_ingredients) == 0:
            raise serializers.ValidationError({
                'ingredients': 'Попытка передать пустой список ингредиентов!'
            })
        elif len(ingredients) != len(uniq_ingredients):
            raise serializers.ValidationError({
                'ingredients': 'Попытка добавить идентичные ингредиента.'
            })
        # Проверяем наличие ингредиентов в базе данных и их количество
        for item in value:
            ingredient = item['id']
            amount = item['amount']
            if amount < 1:
                raise serializers.ValidationError({
                    'amount': f'Кол-во ингредиента id {ingredient} < 1.'
                })
            if not Ingredient.objects.filter(pk=ingredient).exists():
                raise serializers.ValidationError({
                    'ingredients': f'Ингредиента с id {ingredient} нет в базе'
                })
        return value

    @transaction.atomic
    def process_ingredients(self, instance, ingredients_data):
        # Создание связей с ингредиентами
        ingredient_recipe_list = []
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id']
            amount = ingredient_data['amount']
            # Получаем объект ингредиента
            ingredient = get_object_or_404(Ingredient, id=ingredient_id)
            # Создаем объект IngredientRecipe и добавляем в список
            ingredient_recipe = IngredientRecipe(
                recipe=instance,
                ingredient=ingredient,
                amount=amount
            )
            ingredient_recipe_list.append(ingredient_recipe)
        # Добавляем все связи в базу данных
        IngredientRecipe.objects.bulk_create(ingredient_recipe_list)

    @transaction.atomic
    def create(self, validated_data):
        # Извлекаем данные о тегах и ингредиентах из валидированных данных
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients')
        # Создание рецепта с автором
        recipe = Recipe.objects.create(**validated_data)
        # Создание связей с тегами
        recipe.tags.set(tags_data)
        # Создание связей с ингредиентами
        self.process_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        # Извлекаем данные о тегах и ингредиентах из валидированных данных
        ingredients_data = validated_data.pop('ingredients', [])
        self.validate_ingredients(ingredients_data)
        tags_data = validated_data.pop('tags', [])
        self.validate_tags(tags_data)
        # Очищаем все связи с тегами и ингредиентами
        instance.tags.clear()
        instance.ingredients.clear()
        # Добавляем новые связи с тегами
        for tag in tags_data:
            instance.tags.add(tag)
        # Создаем новые связи с ингредиентами
        self.process_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class FollowRecipeInsertSerializer(serializers.ModelSerializer):
    """Сабсериалайзер рецептов автора, на кого подписан пользователь."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowCreateListSerializer(serializers.ModelSerializer):
    """Сериалайзер создания подписки."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes_and_limit'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        # Получаем текущего пользователя из контекста запроса
        current_user = self.context['request'].user
        # Проверяем, подписан ли текущий пользователь на пользователя obj
        return obj.followers.filter(follower=current_user).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(
            author=obj
        ).count()

    def get_recipes_and_limit(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(
            author=obj
        ).all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = FollowRecipeInsertSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data


class FavouriteShoplistRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер ответа на добавление рецепта в избранное или шоплист."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
