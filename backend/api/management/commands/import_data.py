import csv

from django.core.management.base import BaseCommand

from api.models import Ingredient, Tag
from api.constants import MIN_COLUMNS


class Command(BaseCommand):
    help = 'Импортирует данные из CSV файлов для ингредиентов и тегов'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ingredients',
            type=str,
            help='Путь к CSV-файлу с ингредиентами'
        )
        parser.add_argument(
            '--tags',
            type=str,
            help='Путь к CSV-файлу с тегами'
        )

    def handle(self, *args, **kwargs):
        ingredients_file = kwargs['ingredients']
        tags_file = kwargs['tags']

        if ingredients_file:
            ingredients = []
            with open(ingredients_file, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= MIN_COLUMNS:
                        name, measurement_unit = row
                        if name:
                            ingredients.append(Ingredient(
                                name=name,
                                measurement_unit=measurement_unit
                            ))
            Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
            self.stdout.write(
                self.style.SUCCESS('Ингредиенты успешно импортированы!')
            )

        if tags_file:
            tags = []
            with open(tags_file, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= MIN_COLUMNS:
                        name, slug = row
                        if name:
                            tags.append(Tag(name=name, slug=slug))
            Tag.objects.bulk_create(tags, ignore_conflicts=True)
            self.stdout.write(
                self.style.SUCCESS('Теги успешно импортированы!')
            )

        self.stdout.write(self.style.SUCCESS('Данные успешно импортированы!'))
