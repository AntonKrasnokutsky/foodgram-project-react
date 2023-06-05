from django_filters.rest_framework import CharFilter, FilterSet
from recipes.models import Ingredients


class IngredientsFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredients
        fields = ['name', ]
