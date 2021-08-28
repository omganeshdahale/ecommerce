from django.contrib import admin
from .models import *

admin.site.register(Category)

class ProductImageInline(admin.TabularInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'slug',
        'price',
        'discount_price',
        'available',
        'created',
        'updated'
    ]
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'discount_price', 'available']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'get_total_cost',
        'placed',
        'paid',
    ]
    list_filter = ['placed', 'paid']
    inlines = [OrderItemInline]


@admin.register(OrderDetails)
class OrderDetailsAdmin(admin.ModelAdmin):
    list_display = [
        'order',
        'first_name',
        'last_name',
        'phone',
    ]
