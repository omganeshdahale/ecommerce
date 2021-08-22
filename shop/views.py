from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import ProductFilterForm, AddToCartForm, PRODUCT_FILTER_INITIAL
from .models import Category, Product, Order, OrderItem
from .utils import get_filtered_products

def home(request):
    products = Product.objects.filter(available=True)[:8]
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'shop/home.html', context)

def product_list(request):
    get = request.GET.dict()
    page = get.pop('page', None)

    # create form instance with get data if exists else use default
    form = ProductFilterForm(get if get else PRODUCT_FILTER_INITIAL)
    if form.is_valid():
        products = get_filtered_products(form.cleaned_data)

    # pagination
    paginator = Paginator(products, 9)
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

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    context = {
        'product': product,
        'form': AddToCartForm(),
    }
    return render(request, 'shop/product_detail.html', context)

@require_POST
@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = AddToCartForm(request.POST)
    if form.is_valid():
        order, c = Order.objects.get_or_create(
            user=request.user,
            placed=None
        )
        item, c = OrderItem.objects.get_or_create(
            order=order,
            product=product,
            defaults={'quantity': form.cleaned_data['quantity']}
        )
        if not c:
            item.quantity += form.cleaned_data['quantity']
            item.save()
        messages.success(request, 'Added to cart.')

    return redirect('shop:product_detail', slug=product.slug)
