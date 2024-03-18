import json

from django.core.management.base import BaseCommand
from foodgram_backend import settings
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Импортирование даты JSON в модель Джанго'

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR

        self.stdout.write(
            self.style.SUCCESS('Импортирование данных. Тэги. v.1...')
        )

        with open(
            f'{data_path}/data/tags.json', 'r', encoding='utf-8'
        ) as file:
            tags_data = json.load(file)
            for item in tags_data:
                # Проверяем, существует ли ингредиент с таким именем в базе
                existing_tags = Tag.objects.filter(
                    slug=item['slug']
                ).first()
                if existing_tags:
                    self.stdout.write(self.style.WARNING(
                        f'Тэг "{item["slug"]}" уже в базе. Пропускаем.'
                    ))
                    continue

                # Создаем экземпляр модели Tag и сохраняем его
                tag_instance = Tag(**item)
                tag_instance.save()

        self.stdout.write(
            self.style.SUCCESS('Импортирование тэгов завершено.')
        )
