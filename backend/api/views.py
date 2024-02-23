from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        SAFE_METHODS)
from rest_framework.response import Response

from api.paginations import CustomPagination
from api.filters import RecipeFilter, SearchIngredientsFilter
from api.permissions import IsAuthorOrReadOnlyPermission
from api.renders import ShoppingCartDataRenderer
from api.serializers import (CreateFollowSerializer, CreateRecipeSerializer,
                             FavoriteSerializers, IngredientsSerializer,
                             ReadRecipeSerializer,
                             ReadRecipesIngredientsSerializer,
                             ReadUserSerializer,
                             ShoppingCartSerializers, TagSerializer,
                             UserSerializer)
from djoser.views import UserViewSet
from users.models import User, UserSubscribe
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shopping_Cart, Tag)


class RecipesViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ReadRecipeSerializer
        return CreateRecipeSerializer

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'author': request.user.id,
            'recipe': recipe.id
        }
        serializer = ShoppingCartSerializers(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        shopping_cart = Shopping_Cart.objects.filter(
            author=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk)
        )
        if shopping_cart.exists():
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        renderer_classes=(ShoppingCartDataRenderer,)
    )
    def download_shopping_cart(self, request):
        queryset = RecipeIngredient.objects.filter(
            recipes__shopping_cart__author=request.user.id
        )
        file_name = f'Shopping List.{request.accepted_renderer.format}'
        serializer = ReadRecipesIngredientsSerializer(queryset, many=True)
        return Response(serializer.data, headers={
            "Content-Disposition":
            f'attachment; filename="{file_name}"'
        }
        )

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'author': request.user.id,
            'recipe': recipe.id
        }
        serializer = FavoriteSerializers(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        favorite = Favorite.objects.filter(
            author=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk))
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet для работы с тэгами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]
    pagination_class = None


class IngredientsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [AllowAny, ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SearchIngredientsFilter
    pagination_class = None


class UserViewSet(UserViewSet):
    """ViewSet для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = ReadUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=['GET'],
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = get_object_or_404(User, id=self.request.user.id)
        serializer = ReadUserSerializer(
            user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['POST'],
        url_name='subscribe',
        url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):

        context = {'request': request}
        usersubscribe = get_object_or_404(User, id=id)
        data = {
            'author': usersubscribe.id,
            'follower': request.user.id
        }
        serializer = CreateFollowSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def destroy_subscribe(self, request, id):
        subscribe = UserSubscribe.objects.filter(
            author_id=get_object_or_404(User, id=id),
            follower=request.user.id
        )
        if subscribe.exists():
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        url_name='subscriptions',
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            following__follower=self.request.user.id
        )
        pages = self.paginate_queryset(queryset)
        serializer = UserSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
