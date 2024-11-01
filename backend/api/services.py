from django.http import HttpResponse
from urlshortner.utils import shorten_url
from urlshortner.models import Url

from api.models import RecipeIngredient


def generate_short_link(request, recipe_id):
    domain = request.build_absolute_uri().replace(request.get_full_path(), '')
    recipe_url = f'{domain}/recipes/{recipe_id}/'
    
    short_url = Url.objects.filter(url=recipe_url).first()
    if short_url:
        short_link = f'{domain}/s/{short_url.short_url}/'
        return short_link
    
    short_code = shorten_url(recipe_url, is_permanent=False)
    short_link = f'{domain}/s/{short_code}'
    
    return short_link
    

def list_to_txt(user):
    text_shop_list = 'Список покупок \n\n'
    measurement_unit = {}
    ingridient_amount = {}
    ingridients = RecipeIngredient.objects.filter(
        recipe__shoping_list__user=user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit', 'amount')
    for ingredient in ingridients:
        if ingredient['ingredient__name'] in ingridient_amount:
            ingridient_amount[
                ingredient['ingredient__name']
            ] += ingredient['amount']
        else:
            measurement_unit[
                ingredient['ingredient__name']
            ] = ingredient['ingredient__measurement_unit']
            ingridient_amount[
                ingredient['ingredient__name']
            ] = ingredient['amount']
    for ingredient, amount in ingridient_amount .items():
        text_shop_list += (
            f'{ingredient} - {amount}'
            f'{measurement_unit[ingredient]}\n'
        )
    response = HttpResponse(text_shop_list, content_type='text/plain')
    response[
        'Content-Disposition'
    ] = 'attachment; filename="shopping_list.txt"'
    return response
