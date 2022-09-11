from http import HTTPStatus

from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    Cart, Fav, Ingredient, IngredientRecipe, Recipe, Tag)
from users.models import Follow, User
from api.filters import RecipeFilter, IngredientFilter
from api.pagination import PageLimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CartSerializer,
    FavSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    RecipeSmallSerializer,
    TagSerializer,
    UserSerializer,
)
from api.mixins import CreateDestroyViewSet


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageLimitPagination


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PageLimitPagination

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        author = get_object_or_404(
            User,
            id=self.kwargs.get('author_id')
        )
        if author == request.user:
            return Response(
                'Нельзя подписываться на себя',
                status=HTTPStatus.BAD_REQUEST
            )
        try:
            Follow.objects.create(author=author, user=self.request.user)
        except IntegrityError:
            return Response(
                'Вы уже подписаны на данного автора',
                status=HTTPStatus.BAD_REQUEST
            )
        follow = get_object_or_404(
            Follow,
            author=author,
            user=request.user
        )
        serializer = FollowSerializer(follow, many=False)
        return Response(
            data=serializer.data,
            status=HTTPStatus.CREATED
        )

    def delete(self, request, *args, **kwargs):
        author = get_object_or_404(
            User,
            id=self.kwargs.get('author_id')
        )
        get_object_or_404(
            Follow,
            author=author,
            user=request.user
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend, IngredientFilter)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag. objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class FavViewSet(CreateDestroyViewSet):
    serializer_class = FavSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Fav.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('recipe_id')
        )
        Fav.objects.create(
            user=request.user,
            recipe=recipe
        )
        serializer = RecipeSmallSerializer(
            recipe,
            many=False
        )
        return Response(
            data=serializer.data,
            status=HTTPStatus.CREATED
        )

    def delete(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('recipe_id')
        )
        get_object_or_404(
            Fav,
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('recipe_id')
        )
        try:
            Cart.objects.create(user=self.request.user, recipe=recipe)
        except IntegrityError:
            return Response(
                'Этот рецепт уже в списке покупок',
                status=HTTPStatus.BAD_REQUEST
            )
        serializer = RecipeSmallSerializer(recipe, many=False)
        return Response(data=serializer.data, status=HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            id=self.kwargs.get('recipe_id')
        )
        get_object_or_404(
            Cart,
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class ShoppingListViewSet(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        carts = Cart.objects.filter(user=user)
        recipes = [cart.recipe for cart in carts]
        cart = {}
        for recipe in recipes:
            for ingredient in recipe.ingredients.all():
                amount = get_object_or_404(
                    IngredientRecipe,
                    recipe=recipe,
                    ingredient=ingredient
                ).amount
                if ingredient.name not in cart:
                    cart[ingredient.name] = amount
                else:
                    cart[ingredient.name] += amount
        content = ''
        for item in cart:
            units = get_object_or_404(
                Ingredient,
                name=item
            ).measurement_unit
            content += f'{item}: {cart[item]}{units}\n'
        response = HttpResponse(
            content, content_type='text/plain,charset=utf8'
        )
        response['Content-Disposition'] = 'attachment; filename="cart.txt"'
        return response
