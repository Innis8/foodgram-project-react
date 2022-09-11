from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from recipes.models import (
    Cart, Fav, Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe)
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        import base64
        import uuid

        import six
        from django.core.files.base import ContentFile

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class FavSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fav
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class RecipeSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientRecipeSmallSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password'))
        )
        return super().create(validated_data)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_authenticated
            and Follow.objects.filter(
                user=request.user,
                author__id=obj.id
            ).exists()
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    is_faved = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField(
    )
    tags = TagSerializer(many=True)
    author = UserSerializer(many=False)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredientrecipes'
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_faved(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_authenticated
            and Fav.objects.filter(
                user=request.user,
                recipe__id=obj.id
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_authenticated
            and Cart.objects.filter(
                user=request.user,
                recipe__id=obj.id
            ).exists()
        )


class RecipePostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField(
        max_length=None,
        use_url=False
    )
    ingredients = IngredientRecipeSmallSerializer(
        source='ingredientrecipes',
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    is_faved = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_faved(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_authenticated
            and Fav.objects.filter(
                user=request.user,
                recipe__id=obj.id
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_authenticated
            and Cart.objects.filter(
                user=request.user,
                recipe__id=obj.id
            ).exists()
        )

    def validate_ingredients(self, value):
        ingredients_list = []
        ingredients = value
        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Убедитесь, что количество больше 0')
            check_id = ingredient['ingredient']['id']
            check_ingredient = Ingredient.objects.filter(id=check_id)
            if not check_ingredient.exists():
                raise serializers.ValidationError(
                    'Ингредиент отсутствует')
            if check_ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиент повторяется')
            ingredients_list.append(check_ingredient)
        return value

    def add_tags_and_ingredients(self, tags, ingredients, recipe):
        for tag in tags:
            recipe.tags.add(tag)
            recipe.save()
        for ingredient in ingredients:
            if not IngredientRecipe.objects.filter(
                    ingredient_id=ingredient['ingredient']['id'],
                    recipe=recipe).exists():
                ingredient_recipe = IngredientRecipe.objects.create(
                    ingredient_id=ingredient['ingredient']['id'],
                    recipe=recipe
                )
                ingredient_recipe.amount = ingredient['amount']
                ingredient_recipe.save()
            else:
                IngredientRecipe.objects.filter(
                    recipe=recipe
                ).delete()
                recipe.delete()
                raise serializers.ValidationError(
                    'Ингредиент уже есть в рецепте'
                )
        return recipe

    def create(self, validated_data):
        author = validated_data.get('author')
        name = validated_data.get('name')
        image = validated_data.get('image')
        text = validated_data.get('text')
        ingredients = validated_data.pop('ingredientrecipes')
        tags = validated_data.pop('tags')
        cooking_time = validated_data.get('cooking_time')
        recipe = Recipe.objects.create(
            author=author,
            name=name,
            image=image,
            text=text,
            cooking_time=cooking_time,
        )
        recipe = self.add_tags_and_ingredients(tags, ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredientrecipes')
        tags = validated_data.pop('tags')
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        instance = self.add_tags_and_ingredients(
            tags, ingredients, instance
        )
        super().update(instance, validated_data)
        instance.save()
        return instance


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='author.recipes.count',
        read_only=True
    )

    class Meta:
        model = Follow
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed', 'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request:
            return True
        return (
            Follow.objects.filter(
                user=request.user,
                author__id=obj.id
            ).exists()
            and request.user.is_authenticated
        )

    def get_recipes(self, obj):
        try:
            recipes_limit = int(
                self.context.get('request').query_params['recipes_limit']
            )
            recipes = Recipe.objects.filter(author=obj.author)[:recipes_limit]
        except Exception:
            recipes = Recipe.objects.filter(author=obj.author)
        serializer = RecipeSmallSerializer(recipes, many=True)
        return serializer.data
