from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )

    class Meta:
        abstract = True


class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='following',
        verbose_name='подписчик',
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='followers',
        verbose_name='на кого подписан',
    )

    def __str__(self):
        return f"{self.follower} подписан на {self.following}"

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'


class Tag(BaseModel):
    name = models.CharField(
        max_length=128,
        verbose_name='название',
    )
    color = models.IntegerField(
        verbose_name='цвет',
    )  # уточнить
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'


class Measurement(BaseModel):
    type = models.CharField(
        max_length=128,
        verbose_name='тип',
    )

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = 'единица измерения'
        verbose_name_plural = 'Единицы измерения'


class Ingredient(BaseModel):
    name = models.CharField(
        max_length=256,
        verbose_name='название',
    )
    measurement_unit = models.ForeignKey(
        Measurement, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(BaseModel):
    name = models.CharField(
        max_length=256,
        verbose_name='название',
    )
    tag = models.ManyToManyField(Tag, through='TagRecipe')
    ingredient = models.ManyToManyField(Ingredient, through='IngredientRecipe')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    text = models.TextField(verbose_name='описание',)
    image = models.ImageField(
        upload_to='recipes/', null=True, blank=True
    )  # разобраться
    cooking_time = models.CharField(
        max_length=50,
        verbose_name='время приготовления',
    )  # разобраться с типом поля

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag, on_delete=models.SET_NULL, null=True, related_name='tag_recipes'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='tag_recipes'
    )


class IngredientRecipe(models.Model):
    ingredient_id = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.IntegerField()


class Favourite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.recipe} в избранном {self.user}"

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'изранное'
        verbose_name_plural = 'Избранное'


class Shoplist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.recipe} в списке покупок {self.user}"

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
