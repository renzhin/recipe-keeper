import base64
from django.shortcuts import get_object_or_404
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


class IngredientWriteSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField(source='measurement_unit.type')
    amount = serializers.IntegerField(write_only=True)  # Добавляем поле amount для записи

    class Meta:
        model = Ingredient
        fields = ['id', 'measurement_unit', 'amount']  # Убираем 'name' из списка полей
        read_only_fields = ['name']  # Добавляем 'name' в список read-only полей

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Если ингредиент связан с рецептом, добавляем значение amount в выходные данные
        if 'request' in self.context:
            request = self.context['request']
            ingredient_recipe = instance.ingredient_recipes.filter(recipe_id=request.data.get('id')).first()
            if ingredient_recipe:
                data['amount'] = ingredient_recipe.amount
        return data


class IngredientSubSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField(
        source='measurement_unit.type'
    )
    amount = serializers.SerializerMethodField()
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit', 'amount']

    def get_amount(self, obj):
        # Получаем связанный объект IngredientRecipe для данного ингредиента
        ingredient_recipe = obj.ingredient_recipes.first()  # предполагая, что ингредиент может быть связан только с одной записью IngredientRecipe
        if ingredient_recipe:
            return ingredient_recipe.amount
        return None


class IngredientSub2Serializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ['id', 'amount']

    def get_amount(self, obj):
        # Получаем связанный объект IngredientRecipe для данного ингредиента
        ingredient_recipe = obj.ingredient_recipes.first()  # предполагая, что ингредиент может быть связан только с одной записью IngredientRecipe
        if ingredient_recipe:
            return ingredient_recipe.amount
        return None

# class IngredientSub2Serializer(serializers.ModelSerializer):
#     amount = serializers.IntegerField(source='ingredient_recipes__amount', read_only=True)

#     class Meta:
#         model = Ingredient
#         fields = ['id', 'amount']


class IngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


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


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    author = UserSerializer()
    ingredients = IngredientSubSerializer(many=True, required=False)
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


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientPostSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]

    # def validate_ingredients(self, ingredients):
    #     ingredients_data = []
    #     if not ingredients:
    #         raise serializers.ValidationError(
    #             'Ингредиенты отсутствуют в запросе')
    #     for ingredient in ingredients:
    #         if ingredient['id'] in ingredients_data:
    #             raise serializers.ValidationError(
    #                 'Ингредиенты не длжны поваторяться')
    #         ingredients_data.append(ingredient['id'])
    #         if int(ingredient.get('amount')) < 1:
    #             raise serializers.ValidationError(
    #                 'Ингредиенты отсутсвуют')
    #     return ingredients

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])

        # Создание рецепта с автором
        recipe = Recipe.objects.create(**validated_data)
        print("Печатаем recipe:", recipe)

        # Создание связей с тегами
        for tag in tags_data:
            TagRecipe.objects.create(tag=tag, recipe=recipe)

        # Создание связей с ингредиентами
        print("Печатаем ingredients_data:", ingredients_data)
        for ingredient_data in ingredients_data:
            ingredient_idd = ingredient_data['id']
            amount = ingredient_data['amount']
            print("Печатаем ingredient_idd:", ingredient_idd)

            # Получаем объект ингредиента
            ingredient = get_object_or_404(Ingredient, id=ingredient_data.get('id'))
            print("Печатаем ingredient:", ingredient)
            print("Печатаем amount:", amount)
            # Создаем связь IngredientRecipe
            IngredientRecipe.objects.create(ingredient_id=ingredient, recipe_id=recipe, amount=amount)

        return recipe


# class RecipeSerializer(serializers.ModelSerializer):
#     tags = serializers.PrimaryKeyRelatedField(
#         queryset=Tag.objects.all(),
#         many=True,
#         required=False
#     )
#     author = serializers.PrimaryKeyRelatedField(
#         default=serializers.CurrentUserDefault(),
#         read_only=True
#     )
#     ingredients = IngredientSubSerializer(many=True, required=False)
#     image = Base64ImageField(required=False, allow_null=True)
#     is_favorited = serializers.BooleanField(
#         default=False,
#         read_only=True
#     )
#     is_in_shopping_cart = serializers.BooleanField(
#         default=False,
#         read_only=True,
#     )

#     class Meta:
#         model = Recipe
#         fields = [
#             'id', 'tags', 'author', 'ingredients', 'is_favorited',
#             'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
#         ]

#     def create(self, validated_data):
#         tags_data = validated_data.pop('tags', [])
#         ingredients_data = validated_data.pop('ingredients', [])

#         # Создание рецепта с автором
#         recipe = Recipe.objects.create(**validated_data)

#         # Создание связей с тегами по переданным данным
#         for tag_id in tags_data:
#             tag = Tag.objects.get(id=tag_id)
#             TagRecipe.objects.create(tag=tag, recipe=recipe)

#         # Создание связей с ингредиентами
#         for ingredient in ingredients_data:
#             current_ingredient, status = Ingredient.objects.get_or_create(**ingredient)
#             IngredientRecipe.objects.create(ingredient_id=current_ingredient, recipe_id=recipe)

#         return recipe

