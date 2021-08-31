from django import template
from django.utils.safestring import mark_safe
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

@register.filter
def rating_to_stars(rating):
    return mark_safe(
        '<i class="fas fa-star text-warning"></i>' * int(rating)
        + '<i class="fas fa-star"></i>' * (5 - int(rating))
    )
