from django.contrib import admin

from recipes.models import (
    Cart, Favorite, Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'recipe', 'amount')


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'recipe',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'how_many_times_favorited',)
    search_fields = ('name', 'author', 'cooking_time',)
    list_filter = ('author', 'name', 'tags',)

    def how_many_times_favorited(self, obj):
        return obj.favorites.count()


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
