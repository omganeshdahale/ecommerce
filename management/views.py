import calendar
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Avg, Q, Sum, Value as V
from django.db.models.functions import Concat
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST
from shop.models import (
    Category,
    Product,
    ProductImage,
    Order,
    OrderItem,
    Review,
    CITY_CHOICES
)
from myproject.settings import EMAIL_HOST_USER
from .decorators import group_required
from .forms import *

User = get_user_model()

@login_required
@group_required('admin')
def category_list(request):
    return render(request, 'management/category_list.html', {
        'categories': Category.objects.exclude(deleted=True)
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
    category = get_object_or_404(Category, pk=pk, deleted=False)
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
    category = get_object_or_404(Category, pk=pk, deleted=False)
    if category.products.exclude(items__order__placed=None).exists():
        category.deleted = True
        category.save()
        category.products.exclude(items__order__placed__isnull=False).delete()
        category.products.update(deleted=True)
        OrderItem.objects.filter(
            product__category=category,
            order__placed=None
        ).delete()
    else:
        category.delete()

    messages.success(request, 'Category deleted successfully.')

    return redirect('management:category_list')

@login_required
@group_required('admin')
def product_list(request):
    search = request.GET.get('search', None)
    if search:
        products = Product.objects.exclude(deleted=True).filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    else:
        products = Product.objects.exclude(deleted=True)

    paginator = Paginator(products, 15)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    sales_labels = []
    sales_data = []
    for p in Product.objects.exclude(deleted=True):
        sales = sum(
            i.quantity for i in p.items.all() if i.order.delivered != None
        )
        if sales:
            sales_labels.append(p.name)
            sales_data.append(sales)

    sales_labels = [i for _, i in sorted(
        zip(sales_data, sales_labels),
        reverse=True
    )][:15]
    sales_data.sort(reverse=True)
    sales_data = sales_data[:15]

    ps = Product.objects.exclude(deleted=True).annotate(
        rating=Avg('reviews__rating')
    )
    rating_labels = [p.name for p in ps.order_by('-rating')[:15] if p.rating]
    rating_data = [p.rating for p in ps.order_by('-rating')[:15] if p.rating]

    context = {
        'products': products,
        'sales_labels': sales_labels,
        'sales_data': sales_data,
        'rating_labels': rating_labels,
        'rating_data': rating_data
    }
    return render(request, 'management/product_list.html', context)

@login_required
@group_required('admin')
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = ProductImageModelFormSet(
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
        formset = ProductImageModelFormSet(
            queryset=ProductImage.objects.none()
        )

    context = {
        'form': form,
        'formset': formset
    }
    return render(request, 'management/product_create.html', context)

@login_required
@group_required('admin')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, deleted=False)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        formset = ProductImageInlineFormSet(
            request.POST,
            request.FILES,
            instance=product
        )
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Product saved successfully.')

            return redirect('management:product_edit', pk=pk)
    else:
        form = ProductForm(instance=product)
        formset = ProductImageInlineFormSet(instance=product)

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
    product = get_object_or_404(Product, pk=pk, deleted=False)
    if product.items.exclude(order__placed=None).exists():
        product.deleted = True
        product.save()
        product.items.filter(order__placed=None).delete()
    else:
        product.delete()

    messages.success(request, 'Product deleted successfully.')

    return redirect('management:product_list')

@login_required
@group_required('admin')
def order_list(request):
    search = request.GET.get('search', None)
    if search:
        orders = Order.objects.exclude(placed=None).annotate(
            full_name=Concat(
                'orderdetails__first_name',
                V(' '),
                'orderdetails__last_name'
            )
        ).filter(
            Q(orderdetails__email__icontains=search)
            | Q(full_name__icontains=search)
        )
    else:
        orders = Order.objects.exclude(placed=None)

    paginator = Paginator(orders, 15)
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    bar_labels = []
    bar_data = []
    for city, city_label in CITY_CHOICES:
        income = Order.objects.exclude(delivered=None).filter(
            orderdetails__city=city
        ).aggregate(Sum('items__cost'))['items__cost__sum']
        if income:
            bar_labels.append(city_label)
            bar_data.append(float(income))

    bar_labels = [i for _, i in sorted(
        zip(bar_data, bar_labels),
        reverse=True
    )][:15]
    bar_data.sort(reverse=True)
    bar_data = bar_data[:15]

    line_labels = []
    line_data = []
    now = timezone.now()

    for m in range(now.month-11, now.month+1):
        y = now.year if m > 0 else now.year - 1
        m = m if m > 0 else 12 + m

        line_labels.append(calendar.month_name[m])
        income = Order.objects.filter(
            delivered__month=m,
            delivered__year=y
        ).aggregate(Sum('items__cost'))['items__cost__sum']
        line_data.append(float(income) if income else 0)

    income = Order.objects.exclude(delivered=None).aggregate(
        Sum('items__cost')
    )['items__cost__sum']
    if not income:
        income = 0
    orders_pending = Order.objects.exclude(placed=None).filter(
        dispatched=None,
        rejected=None
    ).count()
    deliveries_pending = Order.objects.exclude(dispatched=None).filter(
        delivered=None,
        rejected=None
    ).count()
    orders_done = Order.objects.exclude(delivered=None).count()

    context = {
        'orders': orders,
        'bar_labels': bar_labels,
        'bar_data': bar_data,
        'line_labels': line_labels,
        'line_data': line_data,
        'income': income,
        'orders_pending': orders_pending,
        'deliveries_pending': deliveries_pending,
        'orders_done': orders_done
    }
    return render(request, 'management/order_list.html', context)

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
    search = request.GET.get('search', None)
    if search:
        reviews = Review.objects.exclude(product__deleted=True).annotate(
            full_name=Concat('user__first_name', V(' '), 'user__last_name')
        ).filter(
            Q(user__username__icontains=search)
            | Q(user__email__icontains=search)
            | Q(full_name__icontains=search)
            | Q(product__name__icontains=search)
        )
    else:
        reviews = Review.objects.exclude(product__deleted=True)

    paginator = Paginator(reviews, 15)
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
    review = get_object_or_404(Review, pk=pk, product__deleted=False)
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
    search = request.GET.get('search', None)
    if search:
        users = User.objects.annotate(
            full_name=Concat('first_name', V(' '), 'last_name')
        ).filter(
            Q(username__icontains=search)
            | Q(email__icontains=search)
            | Q(full_name__icontains=search)
        )
    else:
        users = User.objects.all()

    paginator = Paginator(users.order_by('date_joined'), 25)
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
    orders = user.orders.exclude(placed=None)

    context = {
        'user': user,
        'orders': orders
    }
    return render(request, 'management/user_detail.html', context)