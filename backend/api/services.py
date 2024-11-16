from collections import defaultdict

from django.http import HttpResponse
from urlshortner.utils import shorten_url
from urlshortner.models import Url

from api.models import RecipeIngredient


def generate_short_link(request, pk):
    base_domain = request.build_absolute_uri(
    ).replace(request.get_full_path(), '')

    recipe_url = f'{base_domain}/recipes/{pk}/'

    existing_short_url = Url.objects.filter(url=recipe_url).first()
    if existing_short_url:
        short_link = base_domain.replace(
            request.get_full_path(), ''
        ) + '/s/' + existing_short_url.short_url
        return short_link

    recipe_url = shorten_url(recipe_url, is_permanent=False)
    short_link = base_domain.replace(
        request.get_full_path(), ''
    ) + '/s/' + recipe_url
    return short_link


def list_to_txt(user):
    text_shop_list = 'Список покупок \n\n'
    ingredient_data = defaultdict(lambda: {'amount': 0, 'unit': ''})

    ingredients = RecipeIngredient.objects.filter(
        recipe__shoping_list__user=user
    ).values('ingredient__name', 'ingredient__measurement_unit', 'amount')

    for ingredient in ingredients:
        name = ingredient['ingredient__name']
        ingredient_data[name]['amount'] += ingredient['amount']
        ingredient_data[name]['unit'] = (
            ingredient['ingredient__measurement_unit']
        )

    for ingredient, data in ingredient_data.items():
        text_shop_list += f"{ingredient} - {data['amount']} {data['unit']}\n"

    response = HttpResponse(text_shop_list, content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.txt"'
    )
    return response
