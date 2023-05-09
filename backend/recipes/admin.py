from django.contrib import admin

from .models import (Favorites, Ingredients, RecipeIngredients, Recipes,
                     RecipesTag, Subscriptions, Tags)


class IngredientsAdmin(admin.ModelAdmin):
    model = Ingredients
    list_display = ['name', ]
    list_filter = ['name', ]
    search_fields = ['name', ]


class TagsAdmin(admin.ModelAdmin):
    model = Tags
    list_display = ['name', 'color', ]
    list_filter = ['name', ]
    search_fields = ['name', ]


class RecipesAdmin(admin.ModelAdmin):
    model = Recipes
    list_display = ['name', 'author', ]


admin.site.register(Favorites)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(RecipesTag)
admin.site.register(RecipeIngredients)
admin.site.register(Subscriptions)
