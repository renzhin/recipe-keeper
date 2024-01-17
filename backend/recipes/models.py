from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


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
        return f"{self.user} подписан на {self.following}"


class Recipe(models.Model):
    name = models.CharField(max_length=256)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    text = models.TextField()
    image = models.ImageField(
        upload_to='recipes/', null=True, blank=True
    )  # разобраться
    cooking_time = models.CharField(max_length=256)  # разобраться с типом поля
    created_at = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )


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
