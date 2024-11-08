import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Import ingredients and tags from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ingredients',
            type=str,
            help='Path to ingredients CSV file'
        )
        parser.add_argument('--tags', type=str, help='Path to tags CSV file')

    @transaction.atomic
    def handle(self, *args, **options):
        ingredients_path = options['ingredients']
        tags_path = options['tags']

        if ingredients_path:
            try:
                with open(
                    ingredients_path, newline='', encoding='utf-8'
                ) as csvfile:
                    reader = csv.DictReader(csvfile)
                    Ingredient.objects.all().delete()
                    Ingredient.objects.bulk_create([
                        Ingredient(
                            name=row['name'],
                            measurement_unit=row['measurement_unit']
                        )
                        for row in reader
                    ])
                self.stdout.write(
                    self.style.SUCCESS('Ingredients imported successfully.')
                )
            except Exception as e:
                raise CommandError(f'Error importing ingredients: {e}')

        if tags_path:
            try:
                with open(tags_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    Tag.objects.all().delete()  # Clear existing data if needed
                    Tag.objects.bulk_create([
                        Tag(name=row['name'], slug=row['slug'])
                        for row in reader
                    ])
                self.stdout.write(
                    self.style.SUCCESS('Tags imported successfully.')
                )
            except Exception as e:
                raise CommandError(f'Error importing tags: {e}')
