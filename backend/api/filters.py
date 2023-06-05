from django_filters.rest_framework import CharFilter, FilterSet
from recipes.models import Ingredients, Recipes


class IngredientsFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredients
        fields = ['name', ]


class RecipesFilter(FilterSet):
    tags = CharFilter(field_name='tag__name', )

    class Meta:
        model = Recipes
        fields = ['tags', ]
