from http import HTTPStatus
from pathlib import Path
from fpdf import FPDF

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorites, Ingredients, Recipes, ShoppingCart,
                            Subscriptions, Tags)
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination

from .serializers import (FavoritesSerializer, IngredientsSerializer,
                          RecepiesSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, TagsSerializer)

User = get_user_model()


class IngredientsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['name', ]


class TagsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class FavoritesViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = FavoritesSerializer
    pagination_class = None

    @property
    def recipe(self):
        return get_object_or_404(Recipes, pk=self.kwargs.get('recipe_id'))

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.request.user)
        return user.favorites.all()

    def create(self, request, *args, **kwargs):
        if Favorites.objects.filter(
            recipe=self.recipe,
            user=self.request.user
        ).exists():
            data = {
                'error': 'Рецепт уже в избранном.'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        if not serializer.is_valid():
            return super().permission_denied(self.request)

        serializer.save(recipe_id=self.recipe.id, user_id=self.request.user.id)

    def destroy(self, request, *args, **kwargs):
        try:
            favorite = Favorites.objects.get(
                recipe=self.recipe,
                user=self.request.user
            )
            favorite.delete()
        except Favorites.DoesNotExist:
            data = {
                'error': 'Рецепта нет в избранном.'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({}, status=HTTPStatus.NO_CONTENT)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecepiesSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author', )    # 'tags')


class SubscribeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pagination_class = LimitOffsetPagination
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return self.request.user.publisher.all()

    @property
    def author(self):
        return get_object_or_404(User, pk=self.kwargs.get('author_id'))

    def create(self, request, *args, **kwargs):
        if self.author == self.request.user:
            data = {
                'error': 'Нельзя подписаться на себя..'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
        if Subscriptions.objects.filter(
            author=self.author,
            user=self.request.user
        ).exists():
            data = {
                'error': 'Подписка на автора активна.'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        print(self.author.id)
        print(self.author.email)
        if not serializer.is_valid():
            return super().permission_denied(self.request)

        serializer.save(author=self.author, user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            subscriptions = Subscriptions.objects.get(
                author=self.author,
                user=self.request.user
            )
            subscriptions.delete()
        except Subscriptions.DoesNotExist:
            data = {
                'error': 'Вы не подписаны на автора.'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({}, status=HTTPStatus.NO_CONTENT)


class ShoppingCartViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ShoppingCartSerializer
    pagination_class = None

    @property
    def recipe(self):
        return get_object_or_404(Recipes, pk=self.kwargs.get('recipe_id'))

    @property
    def get_ingridients(self, *args, **kwargs):
        recipes = self.request.user.shopping_cart.filter()
        ingredients = {}
        for recipe in recipes:
            for recipe_ingredient in recipe.recipe.ingredients.all():
                if recipe_ingredient.ingredient in ingredients:
                    ingredients[
                        recipe_ingredient.ingredient
                    ] += recipe_ingredient.amount
                else:
                    ingredients[
                        recipe_ingredient.ingredient
                    ] = recipe_ingredient.amount
        return ingredients

    def create_pdf(self, ingredients, *args, **kwargs):
        result_file = Path("output.pdf")

        print(ingredients)
        pdf = FPDF(format='a4', unit='mm')
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'DejaVuSerif.ttf', uni=True)
        pdf.set_font('DejaVu', size=14)
        # with pdf.table() as table:
        #     for ingredient, amount in ingredients.items():
        #         data_row = [ingredient.name, ingredient.measurement_unit, amount]
        #         row = table.row()
        #         for datum in data_row:
        #             row.cell(datum)
        for ingredient, amount in ingredients.items():
            text = f'{ingredient.name}, {ingredient.measurement_unit}: {amount}'
            pdf.cell(200, 10, txt=text, ln=1, align="J")
        print(pdf)
        pdf.output(result_file)

        # pdf = Document()
        # page = Page()
        # pdf.add_page(page)
        # layout = SingleColumnLayout(page)
        # for ingredient, amount in ingredients.items():
        #     text = f'{amount}'
        #     layout.add(Paragraph(text, font='Times-Roman', font_size=Decimal(20)))
        #     # print(ingredient, amount)

        # print(result_file)
        # with open(Path(result_file), "wb") as pdf_file_handle:
        #     PDF.dumps(pdf_file_handle, pdf)
        return result_file

    def list(self, *args, **kwargs):
        shopping_cart = self.create_pdf(self.get_ingridients)
        print(shopping_cart)
        return super().list(self.request, *args, **kwargs)
        # return self.create_pdf()

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.request.user.id)
        return user.shopping_cart.all()

    def create(self, request, *args, **kwargs):
        if ShoppingCart.objects.filter(
            recipe=self.recipe,
            user=self.request.user
        ).exists():
            data = {
                'error': 'Рецепт уже в списке покупок.'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        if not serializer.is_valid():
            return super().permission_denied(self.request)

        serializer.save(recipe_id=self.recipe.id, user_id=self.request.user.id)

    def destroy(self, request, *args, **kwargs):
        try:
            favorite = ShoppingCart.objects.get(
                recipe=self.recipe,
                user=self.request.user
            )
            favorite.delete()
        except Favorites.DoesNotExist:
            data = {
                'error': 'Рецепта нет в списке покупок.'
            }
            return JsonResponse(data, status=HTTPStatus.BAD_REQUEST)
        return JsonResponse({}, status=HTTPStatus.NO_CONTENT)
