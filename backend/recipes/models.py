from colorfield.fields import ColorField
from django.db import models

from core.basemodel import AuthorRecipeModel
from core.constants import (LENGTH_FOR_MEASUREMENT_UNIT, LENGTH_FOR_NAME,
                            MAX_VALUE, MIN_VALUE, ROW_LIMIT_TO)
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import User


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        max_length=LENGTH_FOR_NAME,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=LENGTH_FOR_MEASUREMENT_UNIT,
        verbose_name='Единицы измерения',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('name', 'measurement_unit',),
                                    name='unique_ingredient'),
        )
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:ROW_LIMIT_TO]


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=LENGTH_FOR_NAME,
        verbose_name='Название'
    )
    color = ColorField(
        format='hex',
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name[:ROW_LIMIT_TO]


class Recipe(models.Model):
    """Модель рецептов."""

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to='media/',
        verbose_name='Фото'
    )
    name = models.CharField(
        max_length=LENGTH_FOR_NAME,
        verbose_name='Название'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки',
        validators=[
            MinValueValidator(
                MIN_VALUE, message=('Убедитесь, что введенное '
                                    f'число больше или равно {MIN_VALUE}')
            ),
            MaxValueValidator(
                MAX_VALUE, message=('Убедитесь, что введенное '
                                    f'число меньше или равно {MAX_VALUE}')
            )
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name[:ROW_LIMIT_TO]


class RecipeIngredient(models.Model):
    """Промежуточная модель для Рецептов и Игредиентов."""

    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipesingredients',
        verbose_name='Рецепт')
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN_VALUE, message=('Убедитесь, что введенное '
                                    f'число больше или равно {MIN_VALUE}')
            ),
            MaxValueValidator(
                MAX_VALUE, message=('Убедитесь, что введенное '
                                    f'число меньше или равно {MAX_VALUE}')
            )
        ],
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('recipes', 'ingredients',),
                                    name='unique_recipe_with_ingredients'),
        )
        ordering = ['recipes']
        verbose_name = 'Игредиент'
        verbose_name_plural = 'Количество ингридиентов'

    def __str__(self):
        return f'{self.recipes} ингредиенты: {self.ingredients}'


class Shopping_Cart(AuthorRecipeModel):
    """Модель для добавления рецепта в список покупок."""

    class Meta:
        default_related_name = 'shopping_list'
        ordering = ['recipe']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.author} : {self.recipe}'


class Favorite(AuthorRecipeModel):
    """Модель для добавления рецепта в избранное."""

    class Meta:
        default_related_name = 'favorites'
        ordering = ['recipe']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.author} : {self.recipe}'
