from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import modelformset_factory, inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST
from shop.models import Category, Product, ProductImage, Order, Review
from myproject.settings import EMAIL_HOST_USER
from .decorators import group_required
from .forms import *

User = get_user_model()

@login_required
@group_required('admin')
def category_list(request):
    return render(request, 'management/category_list.html', {
        'categories': Category.objects.all()
    })

@login_required
@group_required('admin')
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')

            return redirect('management:category_list')
    else:
        form = CategoryForm()

    return render(request, 'management/category_create.html', {'form': form})

@login_required
@group_required('admin')
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category saved successfully.')

            return redirect('management:category_edit', pk=pk)
    else:
        form = CategoryForm(instance=category)

    context = {
        'category': category,
        'form': form
    }
    return render(request, 'management/category_edit.html', context)

@require_POST
@login_required
@group_required('admin')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully.')

    return redirect('management:category_list')

@login_required
@group_required('admin')
def product_list(request):
    paginator = Paginator(Product.objects.all(), 15)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'management/product_list.html', {
        'products': products
    })

@login_required
@group_required('admin')
def product_create(request):
    ProductImageFormSet = modelformset_factory(
        ProductImage,
        form=ProductImageForm,
        extra=3
    )
    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(
            request.POST,
            request.FILES,
            queryset=ProductImage.objects.none()
        )
        if form.is_valid() and formset.is_valid():
            product = form.save()
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    ProductImage(product=product, image=image).save()

            messages.success(request, 'Product created successfully.')

            return redirect('management:product_list')
    else:
        form = ProductForm()
        formset = ProductImageFormSet(queryset=ProductImage.objects.none())

    context = {
        'form': form,
        'formset': formset
    }
    return render(request, 'management/product_create.html', context)

@login_required
@group_required('admin')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    ProductImageFormSet = inlineformset_factory(
        Product,
        ProductImage,
        form=ProductImageForm,
        extra=1
    )
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Product saved successfully.')

            return redirect('management:product_edit', pk=pk)
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)

    context = {
        'product': product,
        'form': form,
        'formset': formset
    }
    return render(request, 'management/product_edit.html', context)

@require_POST
@login_required
@group_required('admin')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Product deleted successfully.')

    return redirect('management:product_list')

@login_required
@group_required('admin')
def order_list(request):
    paginator = Paginator(Order.objects.exclude(placed__isnull=True), 15)
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    return render(request, 'management/order_list.html', {
        'orders': orders
    })

@login_required
@group_required('admin')
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, placed__isnull=False)
    if request.method == 'POST' and not order.paid:
        form = OrderRejectForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            order.rejected = timezone.now()
            order.save()

            subject = f'Order with id {order.id} rejected'
            html = render_to_string('email/rejected.html', {'order': order})
            plain = strip_tags(html)
            from_ = EMAIL_HOST_USER
            to = [order.orderdetails.email]

            send_mail(subject, plain, from_,
                to, html_message=html)

            messages.success(request, 'Order rejected')

            return redirect('management:order_detail', pk=pk)
    else:
        form = OrderRejectForm(instance=order)

    context = {
        'order': order,
        'form': form
    }
    return render(request, 'management/order_detail.html', context)

@login_required
@group_required('admin')
def order_dispatch(request, pk):
    order = get_object_or_404(Order, pk=pk, placed__isnull=False)
    order.dispatched = timezone.now()
    order.save()

    subject = f'Order with id {order.id} dispatched'
    html = render_to_string('email/dispatched.html', {'order': order})
    plain = strip_tags(html)
    from_ = EMAIL_HOST_USER
    to = [order.orderdetails.email]

    send_mail(subject, plain, from_,
        to, html_message=html)

    messages.success(request, 'Order dispatched')

    return redirect('management:order_detail', pk=pk)

@login_required
@group_required('admin')
def order_deliver(request, pk):
    order = get_object_or_404(Order, pk=pk, dispatched__isnull=False)
    if order.orderdetails.payment_method == 'C':
        order.paid = timezone.now()
    order.delivered = timezone.now()
    order.save()

    subject = f'Order with id {order.id} delivered'
    html = render_to_string('email/delivered.html', {'order': order})
    plain = strip_tags(html)
    from_ = EMAIL_HOST_USER
    to = [order.orderdetails.email]

    send_mail(subject, plain, from_,
        to, html_message=html)

    messages.success(request, 'Order delivered')

    return redirect('management:order_detail', pk=pk)

@login_required
@group_required('admin')
def review_list(request):
    paginator = Paginator(Review.objects.all(), 15)
    page = request.GET.get('page')
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    return render(request, 'management/review_list.html', {
        'reviews': reviews
    })

@require_POST
@login_required
@group_required('admin')
def review_active_toggle(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.active:
        review.active = False
        messages.success(request, f'Review deactivated')
    else:
        review.active = True
        messages.success(request, f'Review activated')

    review.save()

    return redirect('management:review_list')

@login_required
@group_required('admin')
def user_list(request):
    paginator = Paginator(User.objects.all().order_by('date_joined'), 25)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'management/user_list.html', {
        'users': users
    })

@login_required
@group_required('admin')
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    orders = user.orders.exclude(placed__isnull=True)

    context = {
        'user': user,
        'orders': orders
    }
    return render(request, 'management/user_detail.html', context)