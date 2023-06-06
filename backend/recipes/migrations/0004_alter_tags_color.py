# Generated by Django 4.2 on 2023-06-05 11:47

from django.db import migrations, models
import recipes.models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20230601_0926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tags',
            name='color',
            field=models.CharField(max_length=7, unique=True, validators=[recipes.models.validate_tag_color], verbose_name='Цвет'),
        ),
    ]