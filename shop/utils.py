from django.db.models import Q
from .models import Product

def get_filtered_products(cd):
    sort_by = cd.pop('sort_by')
    search = cd.pop('search')
    min_price = cd.pop('min_price')
    max_price = cd.pop('max_price')
    min_rating = cd.pop('min_rating')
    include_out_of_stock = cd.pop('include_out_of_stock')

    if cd['category'] == None:
        cd.pop('category')

    if include_out_of_stock:
        products = Product.objects.exclude(deleted=True).filter(**cd)
    else:
        products = Product.objects.exclude(
            deleted=True
        ).filter(available=True, **cd)

    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    if sort_by == 'price':
        products = list(products)
        products.sort(key=lambda p: p.get_final_price())
    elif sort_by == '-price':
        products = list(products)
        products.sort(key=lambda p: p.get_final_price(), reverse=True)
    elif sort_by == '-rating':
        products = list(products)
        products.sort(key=lambda p: p.get_avg_rating(), reverse=True)
    elif sort_by:
        products = products.order_by(sort_by)

    if min_price != None:
        products = filter(lambda p: p.get_final_price() >= min_price, products)
    if max_price != None:
        products = filter(lambda p: p.get_final_price() <= max_price, products)
    if min_rating:
        products = filter(lambda p: p.get_avg_rating() >= min_rating, products)

    return list(products)
