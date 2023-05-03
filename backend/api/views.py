from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from recipes.models import Ingredients, Tags
from .serializers import IngredientsSerializer, TagsSerializer


class IngredientsViewStet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    http_method_names = ['get', ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['name', ]


class TagsViewStet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    http_method_names = ['get', ]
