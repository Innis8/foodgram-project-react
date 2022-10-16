from django.contrib import admin
from django.contrib.admin import display

from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'cooking_time', 'how_many_times_favorited')
    readonly_fields = ('how_many_times_favorited',)
    search_fields = ('name', 'author__username', 'author__email',)
    list_filter = ('tags',)

    @display(description='Количество в избранных')
    def how_many_times_favorited(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    list_filter = ('measurement_unit',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('recipe__name', 'user__username', 'user__email',)
    list_filter = ('recipe__tags',)


@admin.register(IngredientInRecipe)
class IngredientInRecipe(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    search_fields = (
        'recipe__name', 'recipe__author__username', 'recipe__author__email',)
    list_filter = ('recipe__tags',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = (
        'recipe__name', 'recipe__author__username', 'recipe__author__email',)
    list_filter = ('recipe__tags',)
