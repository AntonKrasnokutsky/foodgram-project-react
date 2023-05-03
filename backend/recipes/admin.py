from django.contrib import admin

from .models import Ingredients, Tags


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


admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tags, TagsAdmin)
