# Generated by Django 3.2.16 on 2024-01-22 20:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoplist',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredient',
            field=models.ManyToManyField(through='recipes.IngredientRecipe', to='recipes.Ingredient'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tag',
            field=models.ManyToManyField(through='recipes.TagRecipe', to='recipes.Tag'),
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='ingredient_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient'),
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='recipe_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.measurement'),
        ),
        migrations.AddField(
            model_name='follow',
            name='follower',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='подписчик'),
        ),
        migrations.AddField(
            model_name='follow',
            name='following',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='followers', to=settings.AUTH_USER_MODEL, verbose_name='на кого подписан'),
        ),
        migrations.AddField(
            model_name='favourite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
        migrations.AddField(
            model_name='favourite',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='shoplist',
            unique_together={('user', 'recipe')},
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together={('follower', 'following')},
        ),
        migrations.AlterUniqueTogether(
            name='favourite',
            unique_together={('user', 'recipe')},
        ),
    ]