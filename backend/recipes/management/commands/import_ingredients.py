import json

from django.core.management.base import BaseCommand
from foodgram_backend import settings
from recipes.models import Measurement, Ingredient


class Command(BaseCommand):
    help = 'Импортирование даты JSON в модель Джанго'

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR

        self.stdout.write(self.style.SUCCESS('Импортирование данных v.4...'))

        with open(
            f'{data_path}/data/ingredients.json', 'r', encoding='utf-8'
        ) as file:
            data = json.load(file)

            for item in data:
                # Проверяем, существует ли ингредиент с таким именем в базе
                existing_ingredient = Ingredient.objects.filter(
                    name=item['name']
                ).first()
                if existing_ingredient:
                    # Если ингредиент с таким именем уже существует,
                    # выводим сообщение и пропускаем его
                    self.stdout.write(self.style.WARNING(
                        f'Ингредиент "{item["name"]}" уже в базе. Пропускаем.'
                    ))
                    continue

                # Получаем или создаем экземпляр модели Measurement
                measurement_inst, created = Measurement.objects.get_or_create(
                    t_name=item['measurement_unit']
                )
                item['measurement_unit'] = measurement_inst
                # Создаем экземпляр модели Ingredient и сохраняем его
                ingredient_instance = Ingredient(**item)
                ingredient_instance.save()

        self.stdout.write(
            self.style.SUCCESS('Импортирование данных завершено.')
        )
