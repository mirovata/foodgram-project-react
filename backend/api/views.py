from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import RecipeFilter, SearchIngredientsFilter
from api.paginations import PageNumberAndLimitPagination
from api.permissions import IsAuthorOrReadOnlyPermission
from api.renders import ShoppingCartDataRenderer
from api.serializers import (CreateFollowSerializer, CreateRecipeSerializer,
                             FavoriteSerializers, IngredientsSerializer,
                             ReadRecipeSerializer,
                             ReadRecipesIngredientsSerializer,
                             ReadUserSerializer,
                             ShoppingCartSerializers, SubscribtionsSerializer,
                             TagSerializer, )
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shopping_Cart, Tag)
from users.models import User, UserSubscribe


class RecipesViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = (
        IsAuthorOrReadOnlyPermission,
        IsAuthenticatedOrReadOnly
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberAndLimitPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ReadRecipeSerializer
        return CreateRecipeSerializer

    def create_favorite_or_shopping_cart(self, request,
                                         pk, serializer_class):
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'author': request.user.id,
            'recipe': recipe.id
        }
        serializer = serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy_favorite_or_shopping_cart(self, request, pk, model):
        model = model.objects.filter(
            author=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk))
        if model.exists():
            model.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.create_favorite_or_shopping_cart(request, pk,
                                                     ShoppingCartSerializers)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        return self.destroy_favorite_or_shopping_cart(request, pk,
                                                      Shopping_Cart)

    @action(
        detail=False,
        methods=['GET'],
        renderer_classes=(ShoppingCartDataRenderer,)
    )
    def download_shopping_cart(self, request):
        queryset = RecipeIngredient.objects.filter(
            recipes__shopping_list__author=request.user.id
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
        return self.create_favorite_or_shopping_cart(request, pk,
                                                     FavoriteSerializers)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        return self.destroy_favorite_or_shopping_cart(request, pk, Favorite)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с тэгами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny,]
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [AllowAny,]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SearchIngredientsFilter
    pagination_class = None


class UserViewSet(UserViewSet):
    """ViewSet для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = ReadUserSerializer
    pagination_class = PageNumberAndLimitPagination

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
        serializer = SubscribtionsSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
