import csv

from django.core.management.base import BaseCommand

from api.models import Ingredient, Tag


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

        with open(ingredients_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    name, measurement_unit = row
                    if name:
                        Ingredient.objects.create(
                            name=name,
                            measurement_unit=measurement_unit
                        )

        with open(tags_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    name, slug = row
                    if name:
                        Tag.objects.create(name=name, slug=slug)

        self.stdout.write(self.style.SUCCESS('Данные успешно импортированы!'))
