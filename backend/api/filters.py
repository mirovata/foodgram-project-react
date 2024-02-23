from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class SearchIngredientsFilter(filters.FilterSet):

    name = filters.CharFilter(
        method='filter_name'
    )

    def filter_name(self, queryset, name, value):
        return queryset.filter(name__istartswith=value.lower())

    class Meta:

        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.NumberFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:

        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorite__author=self.request.user,
            )
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                shopping_cart__author=self.request.user.id,
            )
        return queryset
