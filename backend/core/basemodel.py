from django.db import models

from users.models import User


class AuthorRecipeModel(models.Model):
    """Абстрактная модель.

    Attributes:
        author (ForeignKey):Поле, содержащие pk автора.
        recipe (ForeignKey):Поле, содержащие pk рецепта.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:

        abstract = True
