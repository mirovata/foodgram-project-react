from csv import DictReader

from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag


models = {

    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv'
}


class Command(BaseCommand):

    help = 'Загружает данные из csv в базу'

    def handle(self, *args, **options):

        print('Идет заполнение базы данных:')

        for model, csv_file in models.items():
            with open('data/' + csv_file, encoding='utf-8-sig') as file:
                rows = DictReader(file)
                records = [model(**row) for row in rows]
                model.objects.bulk_create(records)
            self.stdout.write(self.style.SUCCESS(
                f'заполнение модели {model.__name__} завершено.'
            )
            )
