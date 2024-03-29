# Generated by Django 3.2.16 on 2024-02-12 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='favourite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='uniq_favourite'),
        ),
        migrations.AddConstraint(
            model_name='shoplist',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='uniq_shoplist'),
        ),
    ]
