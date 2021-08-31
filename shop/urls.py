from django.urls import path
from .views import *

app_name = 'shop'

urlpatterns = [
    path('', home, name='home'),
    path('shop/', product_list, name='product_list'),
    path('order-history/', order_list, name='order_list'),
    path('invoice/<int:pk>/', invoice, name='invoice'),
    path('cart/', cart, name='cart'),
    path('add-to-cart/<int:pk>/', add_to_cart, name='add_to_cart'),
    path('update-cart/<int:pk>/', update_cart, name='update_cart'),
    path('remove-from-cart/<int:pk>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('success/', success, name='success'),
    path('cancel/', cancel, name='cancel'),
    path('webhooks/stripe/', stripe_webhook, name='stripe_webhook'),
    path('create-review/<int:pk>/', review_create, name='review_create'),
    path('<slug:slug>/', product_detail, name='product_detail'),
]
