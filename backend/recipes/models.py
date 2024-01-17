from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    pass


class Tag(models.Model):
    pass


class RecipeTag(models.Model):
    pass


class Ingredient(models.Model):
    pass


class RecipeIngredient(models.Model):
    pass


class Measurement(models.Model):
    pass


class Favourite(models.Model):
    pass


class Shoplist(models.Model):
    pass
