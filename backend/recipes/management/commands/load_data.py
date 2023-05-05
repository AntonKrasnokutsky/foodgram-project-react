import json
from django.core.management.base import BaseCommand


from recipes.models import Ingredients


class Command(BaseCommand):
    def handle(self, *args, **options):

        with open('../data/ingredients.json', 'rb') as f:
            data = json.load(f)

            for i in data:
                ingredients = Ingredients()
                ingredients.name = i['name']
                ingredients.measurement_unit = i['measurement_unit']
                ingredients.save()
        print('finished')
