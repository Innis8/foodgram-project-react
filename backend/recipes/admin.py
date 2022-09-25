from django.contrib import admin
from django.contrib.admin import display

from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'how_many_times_favorited')
    readonly_fields = ('how_many_times_favorited',)
    search_fields = ('name', 'author', 'cooking_time',)
    list_filter = ('author', 'name', 'tags',)

    @display(description='Количество в избранных')
    def how_many_times_favorited(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)


@admin.register(Favorite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)


@admin.register(IngredientInRecipe)
class IngredientInRecipe(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
