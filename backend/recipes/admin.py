from django.contrib import admin

from .models import (Favorites, Ingredients, RecipeIngredients, Recipes,
                     RecipesTag, Subscriptions, Tags)


class IngredientsAdmin(admin.ModelAdmin):
    model = Ingredients
    list_display = ['name', 'measurement_unit', ]
    list_filter = ['name', ]
    search_fields = ['name', ]


class TagsAdmin(admin.ModelAdmin):
    model = Tags
    list_display = ['name', 'color', ]
    list_filter = ['name', ]
    search_fields = ['name', ]


class RecipesAdmin(admin.ModelAdmin):
    # favorite_count = ('get_favorite_count', )
    model = Recipes
    list_display = ['name', 'author', 'favorite_count', ]
    list_filter = ['author', 'name', 'tags', ]

    def favorite_count(self, obj):
        return obj.favorites.all().count()


admin.site.register(Favorites)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(RecipesTag)
admin.site.register(RecipeIngredients)
admin.site.register(Subscriptions)
