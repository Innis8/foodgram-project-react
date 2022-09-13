from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import (
    CartViewSet,
    FavoriteViewSet,
    FollowViewSet,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingListViewSet,
    TagViewSet,
)

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')


urlpatterns = [
    re_path(
        r'recipes/(?P<recipe_id>\d+)/favorite/',
        FavoriteViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='favorites'
    ),
    re_path(
        r'recipes/(?P<recipe_id>\d+)/shopping_cart/',
        CartViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='shopping_cart'
    ),
    path(
        'users/subscriptions/',
        FollowViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    ),
    path(
        'recipes/download_shopping_cart/',
        ShoppingListViewSet.as_view(),
        name='download'
    ),
    re_path(
        r'users/(?P<author_id>\d+)/subscribe/',
        FollowViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='to_subscribe'
    ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
