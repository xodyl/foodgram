API_VERSION: str = ''
USERNAME_LENGTH: int = 150

MEASUREMENT_UNIT_LENTH: int = 10
MIN_COOKING_TIME: int = 1
MAX_COOKING_TIME: int = 32_000
MIN_INGREDIENT_AMOUNT: int = 1
MAX_INGREDIENT_AMOUNT: int = 32_000
TEXT_FIELD_LENGTH: int = 255

RECIPE_VALIDATION_MESSAGES = {
    'EMPTY': {
        'ingredients': 'Ингридиенты обязательны!',
        'tags': 'Тэги обязательны!'
    },
    'NOT_UNIQUE': {
        'ingredients': 'Ингридиенты не могут повторяться!',
        'tags': 'Тэги не могут повторяться!'
    },
}

MESSAGES = {
    'ALREADY_ADDED': {
        'FAVORITE': 'Рецепт уже добавлен в избранное!',
        'SHOPPING_LIST': 'Рецепт уже добавлен в список покупок!',
    },
    'ADDED_SUCCESS': {
        'FAVORITE': 'Рецепт успешно добавлен в избранное.',
        'SHOPPING_LIST': 'Рецепт успешно добавлен в список покупок.',
    },
    'NOT_FOUND': {
        'FAVORITE': {'errors': 'Рецепт не добавлен в избранное!'},
        'SHOPPING_LIST': {'errors': 'Рецепт не добавлен в список покупок!'},
    },
    'REMOVED_SUCCESS': {
        'FAVORITE': 'Рецепт успешно удален из избранного.',
        'SHOPPING_LIST': 'Рецепт успешно удален из списка покупок.',
    },
}
