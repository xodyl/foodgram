from collections import defaultdict

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
    text_list = 'Список покупок\n\n'
    units = {}
    amounts = defaultdict(int)

    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_list__user=user
    ).values('ingredient__name', 'ingredient__measurement_unit', 'amount')

    for item in ingredients:
        name = item['ingredient__name']
        units[name] = item['ingredient__measurement_unit']
        amounts[name] += item['amount']

    for name, total_amount in amounts.items():
        text_list += f'{name} - {total_amount} {units[name]}\n'

    response = HttpResponse(text_list, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
    return response
