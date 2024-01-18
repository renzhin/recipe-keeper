import json

from django.core.management.base import BaseCommand
from recipes.models import Measurement, Ingredient


class Command(BaseCommand):
    help = 'Import data from JSON file to Django models'

    def handle(self, *args, **options):
        json_file_path = '../data/ingredients.json'

        self.stdout.write(self.style.SUCCESS('Импортирование данных...'))

        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                measurement_instance, created = Measurement.objects.get_or_create(
                    type=item['measurement_unit']
                )
                item['measurement_unit'] = measurement_instance
                ingredient_instance = Ingredient(**item)
                ingredient_instance.save()

        self.stdout.write(self.style.SUCCESS('Импортирование данных завершено.'))
