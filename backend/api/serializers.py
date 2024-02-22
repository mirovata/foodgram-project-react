import djoser.serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shopping_Cart, Tag)
from users.models import User, UserSubscribe


class ReadUserSerializer(djoser.serializers.UserSerializer):
    """Сериализатор для чтения пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'id', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if self.context.get('request').user.is_anonymous:
            return False
        return UserSubscribe.objects.filter(
            author=obj.id,
            follower=request.user.id).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения тэгов."""

    class Meta:

        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов."""

    class Meta:

        model = Ingredient
        fields = '__all__'


class CreateRecipesIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для добавление ингредиентов в рецепты."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class ReadRecipesIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов в рецептах."""

    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class ShoppingCartAndRecipeSerializers(serializers.ModelSerializer):
    """Сериализатор для чтения краткого списка."""

    class Meta:

        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class ShoppingCartSerializers(serializers.ModelSerializer):
    """Сериализатор для создания списка покупок."""

    class Meta:

        model = Shopping_Cart
        fields = '__all__'

    def validate(self, data):

        if not self.context.get('request').method == 'POST':
            return data
        if Shopping_Cart.objects.filter(
            author=data['author'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Вы уже добавили рецепт в список покупок.'
            )
        return data

    def to_representation(self, instance):
        return ShoppingCartAndRecipeSerializers(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class FavoriteSerializers(serializers.ModelSerializer):
    """Сериализатор для создания подписки на рецепт."""

    class Meta:

        model = Favorite
        fields = '__all__'

    def validate(self, data):

        if not self.context.get('request').method == 'POST':
            return data
        if Favorite.objects.filter(
            author=data['author'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Вы уже добавили рецепт в избранное.'
            )
        return data

    def to_representation(self, instance):
        return ShoppingCartAndRecipeSerializers(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""

    ingredients = ReadRecipesIngredientsSerializer(
        many=True,
        source='recipesingredients'
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    image = Base64ImageField(max_length=None)
    author = ReadUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:

        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and Favorite.objects.filter(
                    author=request.user.id,
                    recipe=recipe).exists())

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and Shopping_Cart.objects.filter(
                    author=request.user.id,
                    recipe=recipe
                ).exists())


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    image = Base64ImageField(max_length=None)
    ingredients = CreateRecipesIngredientsSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )

    class Meta:

        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients = data.get('ingredients', [])
        tags = data.get('tags', [])
        if not (ingredients and tags):
            raise serializers.ValidationError(
                'Выберите Тэг или Ингредиент'
            )
        if (len(ingredients) != len(set(ingredient['id']
                                        for ingredient in ingredients)
                                    )
           or len(tags) != len(set(tags))):
            raise serializers.ValidationError(
                'Тэги или ингредиенты не должны повторяться.'
            )
        if any(ingredient.get('amount') == 0 for ingredient in ingredients):
            raise serializers.ValidationError(
                'Время готовки должно быть больше 0 минут.'
            )
        return super().validate(data)

    def create(self, validated_data):

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipes=recipe,
                amount=ingredient['amount'],
                ingredients=ingredient.get('id'), )
        return recipe

    def update(self, recipe, validated_data):

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            for ingredient in ingredients:
                RecipeIngredient.objects.filter(
                    recipes=recipe
                ).delete()
                RecipeIngredient.objects.create(
                   recipes=recipe,
                   amount=ingredient['amount'],
                   ingredients=ingredient.get('id'),
                )
        return recipe

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'recipes_count',
            'is_subscribed',
            'recipes'
        )

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        subscribe = UserSubscribe.objects.filter(
            author=author.id,
            follower=request.user.id).exists()
        return subscribe

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_recipes(self, author):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=author)
        if limit:
            recipes = recipes[: int(limit)]
        serializer = ShoppingCartAndRecipeSerializers(
                recipes, many=True, read_only=True
            )
        return serializer.data


class CreateFollowSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки на пользователя."""

    class Meta:

        model = UserSubscribe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=UserSubscribe.objects.all(),
                fields=('author', 'follower'),
                message='Невозможно подписаться, так как вы уже подписаны'
            )
        ]

    def validate(self, data):
        if data['author'] == data['follower']:
            raise serializers.ValidationError('Невозможно подписаться '
                                              'на самого себя')
        return data

    def to_representation(self, instance):
        return UserSerializer(instance.author, context={
            'request': self.context.get('request')
        }).data
