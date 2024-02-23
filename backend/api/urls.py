from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientsViewSet, RecipesViewSet, TagViewSet,
                       UserViewSet)

routers_v1 = DefaultRouter()

routers_v1.register('recipes', RecipesViewSet, basename='recipes')
routers_v1.register('tags', TagViewSet, basename='tags')
routers_v1.register('ingredients', IngredientsViewSet, basename='ingredients')
routers_v1.register('users', UserViewSet, basename='subscribe')

urlpatterns = [
    path('', include(routers_v1.urls))
]
