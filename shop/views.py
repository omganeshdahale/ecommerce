from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from .forms import ProductFilterForm
from .models import Category, Product

def home(request):
    products = Product.objects.filter(available=True)[:8]
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'shop/home.html', context)

def product_list(request):
    form = ProductFilterForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
        sort_by = cd.pop('sort_by')
        min_price = cd.pop('min_price')
        max_price = cd.pop('max_price')

        if cd['name__icontains'] == None:
            cd.pop('name__icontains')
        if cd['category'] == None:
            cd.pop('category')

        products = Product.objects.filter(**cd)

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

        products = list(products)
    else:
        products = Product.objects.all()

    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'form': form,
        'products': products
    }
    return render(request, 'shop/product_list.html', context)
