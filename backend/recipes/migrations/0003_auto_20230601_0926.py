# Generated by Django 4.2 on 2023-06-01 06:26
import json

from django.db import migrations


def create_ingridients(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Ingredients = apps.get_model('recipes', 'Ingredients')
    with open('data/ingredients.json', 'rb') as f:
        data = json.load(f)

        for i in data:
            Ingredients.objects.using(db_alias).create(
                name=i['name'],
                measurement_unit=i['measurement_unit']
            )

class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(create_ingridients),
    ]
