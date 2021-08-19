from .models import Product

def get_filtered_products(cd):
    sort_by = cd.pop('sort_by')
    min_price = cd.pop('min_price')
    max_price = cd.pop('max_price')
    include_out_of_stock = cd.pop('include_out_of_stock')

    if cd['name__icontains'] == None:
        cd.pop('name__icontains')
    if cd['category'] == None:
        cd.pop('category')

    if include_out_of_stock:
        products = Product.objects.filter(**cd)
    else:
        products = Product.objects.filter(available=True, **cd)

    if sort_by == 'price':
        products = list(products)
        products.sort(key=lambda p: p.get_final_price())
    elif sort_by == '-price':
        products = list(products)
        products.sort(key=lambda p: p.get_final_price(), reverse=True)
    elif sort_by:
        products = products.order_by(sort_by)

    if min_price != None:
        products = filter(lambda p: p.get_final_price() >= min_price, products)
    if max_price != None:
        products = filter(lambda p: p.get_final_price() <= max_price, products)

    return list(products)
