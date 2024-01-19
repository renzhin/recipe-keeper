from rest_framework import serializers

from recipes.models import (
    Follow, Tag, Measurement, Ingredient, Recipe, Favourite, Shoplist, User
)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        models = User
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        models = Follow
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        models = Recipe
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        models = Ingredient
        fields = '__all__'


class MeasurementSerializer(serializers.ModelSerializer):

    class Meta:
        models = Measurement
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        models = Tag
        fields = '__all__'


class FavouriteSerializer(serializers.ModelSerializer):

    class Meta:
        models = Favourite
        fields = '__all__'


class ShoplistSerializer(serializers.ModelSerializer):

    class Meta:
        models = Shoplist
        fields = '__all__'
