from django.contrib import admin

from recipes import models


admin.site.site_header = 'Foodgram'


class IngredientInline(admin.TabularInline):

    model = models.RecipeIngredient
    min_num = 1
    extra = 1


@admin.register(models.Recipe)
class RecipesAdmin(admin.ModelAdmin):

    list_display = (
        'author',
        'name',
        'get_favorite',
        'image',
        'cooking_time'
    )
    list_filter = (
        'name',
        'author',
        'tags'
    )

    inlines = [
        IngredientInline,
    ]

    @admin.display(description='Добавили в избранное')
    def get_favorite(self, obj):
        return obj.favorites.count()


@admin.register(models.Tag)
class TagsAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'color',
        'slug'
    )


@admin.register(models.Ingredient)
class IngredientsAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'measurement_unit'
    )

    list_filter = (
        'name',
    )

    search_fields = (
        'name',
    )


@admin.register(models.Shopping_Cart)
class ShoppingCartAdmin(admin.ModelAdmin):

    list_display = (
        'author',
        'recipe'
    )


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = (
        'author',
        'recipe'
    )
