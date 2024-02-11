from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram_backend.constants import (
    NAME_LONG_NUMBCHAR,
    NAME_MID_NUMBCHAR,
    NAME_SHORT_NUMBCHAR,
    COLOR_NUMBCHAR,
    SLUG_NUMBCHAR
)

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        abstract = True


class Tag(BaseModel):
    name = models.CharField(
        max_length=NAME_SHORT_NUMBCHAR,
        verbose_name='название',
    )
    color = ColorField(
        default='#DDDDDD',
        max_length=COLOR_NUMBCHAR,
        format='hexa',
        verbose_name='цвет',
    )
    slug = models.SlugField(
        max_length=SLUG_NUMBCHAR,
        unique=True,
        verbose_name='слаг',
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Measurement(BaseModel):
    """
    Считаю данную модель необходимой
    для возможности массового переименования
    единиц измерений. Например г. в грм.
    """
    t_name = models.CharField(
        max_length=NAME_SHORT_NUMBCHAR,
        verbose_name='тип',
    )

    class Meta:
        verbose_name = 'единица измерения'
        verbose_name_plural = 'Единицы измерения'

    def __str__(self):
        return self.t_name


class Ingredient(BaseModel):
    name = models.CharField(
        max_length=NAME_LONG_NUMBCHAR,
        verbose_name='название',
    )
    measurement_unit = models.ForeignKey(
        Measurement,
        on_delete=models.CASCADE,
        verbose_name='единицы измерения',
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'name',
                    'measurement_unit'
                ),
                name='uniq_ingredient'
            ),
        )

    def __str__(self):
        return self.name


class Recipe(BaseModel):
    name = models.CharField(
        max_length=NAME_MID_NUMBCHAR,
        verbose_name='название',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='ингредиенты',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор',
    )
    text = models.TextField(verbose_name='описание',)
    image = models.ImageField(
        upload_to='recipes/',
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='время приготовления',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='рецепт',
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='количество',
    )

    class Meta:
        verbose_name = 'ингредиент-рецепт'
        verbose_name_plural = 'Ингредиенты-Рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'ingredient',
                    'recipe'
                ),
                name='uniq_ingredientrecipe'
            ),
        )


class FavouriteShoplist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_users',
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s_recipes',
        verbose_name='рецепт',
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'user',
                    'recipe'
                ),
                name='uniq_favouriteshoplist'
            ),
        )

    def __str__(self):
        return f' {self.recipe} у пользователя {self.user} '


class Favourite(FavouriteShoplist):

    class Meta(FavouriteShoplist.Meta):
        verbose_name = 'изранное'
        verbose_name_plural = 'Избранное'


class Shoplist(FavouriteShoplist):

    class Meta(FavouriteShoplist.Meta):
        verbose_name = 'список покупок'
        verbose_name_plural = 'Список покупок'
