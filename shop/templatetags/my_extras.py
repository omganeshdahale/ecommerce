from django import template
from django.utils.safestring import mark_safe
import markdown
from shop.models import Order

register = template.Library()

@register.filter
def has_group(user, group_name):
    if user.is_superuser:
        return True
    return user.groups.filter(name=group_name).exists()

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

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))

@register.filter
def order_status(order):
    if order.rejected:
        return 'Rejected'
    elif order.delivered:
        return 'Completed'
    elif order.dispatched:
        return 'Dispatched'
    elif order.placed:
        return 'Placed'

@register.filter
def order_status_colour(status):
    if status == 'Rejected':
        return 'danger'
    elif status == 'Completed':
        return 'success'
    elif status == 'Dispatched':
        return 'warning'
    elif status == 'Placed':
        return 'primary'
