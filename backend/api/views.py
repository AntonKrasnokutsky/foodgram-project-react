from rest_framework import mixins, viewsets

from recipes.models import Tags
from .serializers import TagsSerializer


class GetOnlyViewSet(mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    pass


class TagsViewSte(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    http_method_names = ['get', ]
