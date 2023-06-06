from django_filters.rest_framework import CharFilter, FilterSet, filters
from recipes.models import Ingredients, Recipes

# from recipes.models import Tags


class IngredientsFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredients
        fields = ['name', ]


class RecipesFilter(FilterSet):
    # tags = filters.AllValuesMultipleFilter CharFilter(
    #     field_name='tags__tag__slug',
    #     lookup_expr='exact',
    #     exclude=True
    # )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__tag__slug',
        lookup_expr='exact',
        # exclude=True
    )
    # tags = filters.ModelMultipleChoiceFilter(
    #     field_name='tags__slug',
    #     to_field_name='slug',
    #     queryset=Tags.objects.all(),
    # )
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart', ]

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
