from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
import weasyprint
from .forms import *
from .models import Category, Product, Order, OrderItem
from .recommender import Recommender
from .tasks import send_invoice, update_score
from .utils import get_filtered_products

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    products = Product.objects.exclude(
        deleted=True
    ).filter(available=True)[:8]
    categories = Category.objects.exclude(deleted=True)
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
    product = get_object_or_404(Product, slug=slug, deleted=False)
    reviews = product.reviews.filter(active=True).exclude(comment='')
    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)

    # pagination
    paginator = Paginator(reviews, 4)
    page = request.GET.get('page')
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    context = {
        'product': product,
        'reviews': reviews,
        'recommended_products': recommended_products,
        'a_form': AddToCartForm(),
        'r_form': ReviewForm(),
    }
    return render(request, 'shop/product_detail.html', context)

@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, deleted=False)
    if not request.user.is_authenticated:
        return redirect(
            reverse('account_login')
            + '?next='
            + reverse('shop:product_detail', args=[product.slug])
        )

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

@login_required
def cart(request):
    forms = {}
    recommended_products = []
    try:
        order = request.user.orders.get(placed=None)
        items = order.items.all()
        for i in items:
            forms[i.pk] = UpdateCartForm(instance=i)

        r = Recommender()
        recommended_products = r.suggest_products_for(
            [i.product for i in items],
            4
        )

    except Order.DoesNotExist:
        order = None

    context = {
        'order': order,
        'recommended_products': recommended_products,
        'forms': forms
    }
    return render(request, 'shop/cart.html', context)

@require_POST
@login_required
def update_cart(request, pk):
    item = get_object_or_404(OrderItem, pk=pk, order__placed=None)
    form = UpdateCartForm(request.POST, instance=item)
    if form.is_valid():
        form.save()
        messages.success(request, f'Updated {item.product} quantity.')

    return redirect('shop:cart')

@require_POST
@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(OrderItem, pk=pk, order__placed=None)
    item.delete()
    messages.success(request, f'Removed {item.product} from cart.')

    return redirect('shop:cart')

@login_required
def checkout(request):
    try:
        order = request.user.orders.get(placed=None)
        items = order.items.filter(product__available=True)
        if not items.exists():
            return redirect('shop:cart')
    except Order.DoesNotExist:
        return redirect('shop:cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            if hasattr(order, 'orderdetails'):
                order.orderdetails.delete()

            order_details = form.save(commit=False)
            order_details.order = order
            order_details.save()

            if order_details.payment_method == 'C':
                order.place_order()
                send_invoice.delay(order.id)
                update_score.delay(order.id)
            else:
                YOUR_DOMAIN = 'http://localhost:8000'
                line_items = []
                for item in items:
                    line_items.append({
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(
                                item.product.get_final_price() * 100
                            ),
                            'product_data': {
                                'name': item.product.name
                            }
                        },
                        'quantity': item.quantity
                    })

                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=order.pk,
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url=YOUR_DOMAIN + '/success/',
                    cancel_url=YOUR_DOMAIN + '/cancel/',
                )

                return redirect(checkout_session.url)

            return redirect('shop:success')
    else:
        form = CheckoutForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })

    context = {
        'order': order,
        'items': items,
        'form': form
    }
    return render(request, 'shop/checkout.html', context)

def success(request):
    return render(request, 'shop/success.html')

def cancel(request):
    return render(request, 'shop/cancel.html')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        order = Order.objects.get(pk=session['client_reference_id'])
        order.place_order()
        order.paid = timezone.now()
        order.save()
        send_invoice.delay(order.id)
        update_score.delay(order.id)

    return HttpResponse(status=200)

@login_required
def order_list(request):
    context = {
        'orders': request.user.orders.exclude(placed=None)
    }
    return render(request, 'shop/order_list.html', context)

@login_required
def invoice(request, pk):
    order = get_object_or_404(Order, pk=pk, placed__isnull=False)
    if (not request.user.is_superuser
            and not request.user.groups.filter(name='admin').exists()
            and request.user != order.user):
        raise PermissionDenied()

    html = render_to_string('shop/invoice.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'

    weasyprint.HTML(string=html).write_pdf(
        response,
        stylesheets=[
            weasyprint.CSS(
                settings.BASE_DIR / 'static/mystatic/css/invoice.css'
            )
        ]
    )

    return response

@require_POST
@login_required
def review_create(request, pk):
    product = get_object_or_404(Product, pk=pk, deleted=False)
    form = ReviewForm(request.POST)
    if form.is_valid():
        request.user.reviews.filter(product=product).delete()

        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        review.save()

        messages.success(request, 'Review saved.')

    return redirect('shop:product_detail', slug=product.slug)