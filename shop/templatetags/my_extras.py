from django import template
from shop.models import Order

register = template.Library()

@register.filter
def cart_item_count(user):
    try:
        return user.orders.get(placed=None).items.count()
    except Order.DoesNotExist:
        return 0

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
