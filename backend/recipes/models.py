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
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='followers',
    )

    def __str__(self):
        return f"{self.follower} подписан на {self.following}"

    class Meta:
        unique_together = ('follower', 'following')


class Tag(BaseModel):
    name = models.CharField(max_length=128)
    color = models.IntegerField()  # уточнить
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )

    def __str__(self):
        return self.name


class Measurement(BaseModel):
    type = models.CharField(max_length=128)

    def __str__(self):
        return self.type


class Ingredient(BaseModel):
    name = models.CharField(max_length=256)
    measurement_unit = models.ForeignKey(
        Measurement, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Recipe(BaseModel):
    name = models.CharField(max_length=256)
    tag = models.ManyToManyField(Tag, through='TagRecipe')
    ingredient = models.ManyToManyField(Ingredient, through='IngredientRecipe')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    text = models.TextField()
    image = models.ImageField(
        upload_to='recipes/', null=True, blank=True
    )  # разобраться
    cooking_time = models.CharField(max_length=50)  # разобраться с типом поля

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


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
