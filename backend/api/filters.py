import django_filters
from rest_framework import filters
from distutils.util import strtobool

from recipes.models import Recipe, Favorite, Cart

CHOICES = (
    ('0', 'False'),
    ('1', 'True')
)


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name='author__id',)
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug',)
    is_favorited = django_filters.TypedChoiceFilter(
        choices=CHOICES,
        coerce=strtobool,
        method='get_is_favorited'
    )
    is_in_shopping_cart = django_filters.TypedChoiceFilter(
        choices=CHOICES,
        coerce=strtobool,
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        favorites = Favorite.objects.filter(user=self.request.user)
        return queryset.filter(
            pk__in=(favorite.recipe.pk for favorite in favorites)
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        try:
            carts = Cart.objects.filter(user=self.request.user)
        except Cart.DoesNotExist:
            return queryset
        return queryset.filter(
            pk__in=(cart.recipe.pk for cart in carts)
        )


class IngredientFilter(filters.SearchFilter):
    search_param = 'name'
