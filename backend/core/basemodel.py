from django.db import models

from users.models import User


class BaseModel(models.Model):
    """
    Абстрактная модель.
    Добавляет к модели автора и рецепт.
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
