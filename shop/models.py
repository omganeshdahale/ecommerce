from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinLengthValidator,
    RegexValidator,
    MinValueValidator,
    MaxValueValidator
)
from django.db import models
from django.db.models import Avg, Sum
from django.utils import timezone
from django.utils.text import slugify

LABEL_COLOUR_CHOICES = (
    ('P','primary'),
    ('S','secondary'),
    ('Su','success'),
    ('D','danger'),
    ('W','warning'),
    ('I','info'),
)

DIALCODE_CHOICES = (
    ('+91', '+91 (India)'),
)

CITY_CHOICES = (
    ('Ah', 'Ahmednagar'),
    ('Ak', 'Akola'),
    ('Am', 'Amravati'),
    ('Au', 'Aurangabad'),
    ('Be', 'Beed'),
    ('Bh', 'Bhandara'), 
    ('Bu', 'Buldhana'),
    ('Ch', 'Chandrapur'),
    ('Dh', 'Dhule'),
    ('Ga', 'Gadchiroli'),
    ('Go', 'Gondia'),
    ('Hi', 'Hingoli'),
    ('Ja', 'Jalgaon'),
    ('Jan', 'Jalna'),
    ('Ko', 'Kolhapur'),
    ('La', 'Latur'),
    ('Mu', 'Mumbai'),
    ('Ng', 'Nagpur'),
    ('Na', 'Nanded'),
    ('Nab', 'Nandurbar'),
    ('Ns', 'Nashik'), 
    ('Os', 'Osmanabad'),
    ('Pa', 'Parbhani'),
    ('Pu', 'Pune'), 
    ('Ra', 'Raigad'),
    ('Rt', 'Ratnagiri'),
    ('Sa', 'Sangli'),
    ('St', 'Satara'),
    ('Si', 'Sindhudurg'),
    ('So', 'Solapur'), 
    ('Th', 'Thane'),
    ('Wa', 'Washim'),
    ('Ya', 'Yavatmal')
)

PAYMENT_CHOICES = (
    ('S','Stripe'),
    ('C','Cash on Delivery '),
)

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    available = models.BooleanField(default=True)
    label_colour = models.CharField(
        max_length=9,
        choices=LABEL_COLOUR_CHOICES,
        default='P'
    )
    label_text = models.CharField(max_length=20, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_final_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price

    def get_num_rating(self):
        return self.reviews.filter(active=True).count()

    def get_avg_rating(self):
        rating = self.reviews.filter(active=True).aggregate(
            Avg('rating')
        )['rating__avg']

        return rating if rating else 0

    def get_income(self):
        income = self.items.exclude(order__delivered=None).aggregate(
            Sum('cost')
        )['cost__sum']

        return income if income else 0

    def get_sales(self):
        sales = self.items.exclude(order__delivered=None).aggregate(
            Sum('quantity')
        )['quantity__sum']

        return sales if sales else 0

    def get_demand(self):
        demand = self.items.exclude(order__placed=None).filter(
            order__dispatched=None,
            order__rejected=None
        ).aggregate(Sum('quantity'))['quantity__sum']

        return demand if demand else 0

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='product_images/')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True
    )
    placed = models.DateTimeField(null=True, blank=True)
    paid = models.DateTimeField(null=True, blank=True)
    dispatched = models.DateTimeField(null=True, blank=True)
    delivered = models.DateTimeField(null=True, blank=True)
    rejected = models.DateTimeField(null=True, blank=True)
    reject_reason = models.TextField(max_length=1000, blank=True)

    class Meta:
        ordering = ('-placed',)

    @admin.display(description='total cost')
    def get_total_cost(self):
        return sum(i.get_cost() for i in self.items.all())

    def get_total_discount(self):
        return sum(i.get_discount() for i in self.items.all())

    def can_checkout(self):
        return self.items.filter(product__available=True).exists()

    def place_order(self):
        self.placed = timezone.now()
        self.save()

        for item in self.items.filter(product__available=True):
            item.cost = item.get_cost()
            item.save()

        self.items.filter(
            product__available=False
        ).update(order=Order.objects.create(user=self.user))

    def clean(self):
        if not self.placed:
            if self.paid:
                raise ValidationError(
                    "Order can't be paid if its not placed"
                )
            if self.dispatched:
                raise ValidationError(
                    "Order can't be dispatched if its not placed"
                )
            if self.rejected:
                raise ValidationError(
                    "Order can't be rejected if its not placed"
                )
        if not self.dispatched and self.delivered:
            raise ValidationError(
                "Order can't be delivered if its not dispatched"
            )
        if self.paid and self.rejected:
            raise ValidationError(
                "Order can't be rejected if its paid"
            )

    def __str__(self):
        return f'Order #{self.pk}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name='items',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    def get_cost(self):
        if self.cost:
            return self.cost
        elif self.product.available:
            return self.quantity * self.product.get_final_price()
        else:
            return 0

    def get_discount(self):
        if not (self.product.discount_price and self.product.available):
            return 0

        discount = self.product.price - self.product.discount_price
        return self.quantity * discount

    def __str__(self):
        return f'{self.product} x{self.quantity}'


class OrderDetails(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    dial_code = models.CharField(
        max_length=4,
        choices=DIALCODE_CHOICES,
        default='+91',
    )
    phone = models.CharField(
        max_length=15,
        validators=[
            MinLengthValidator(4),
            RegexValidator(
                regex=r'^\d*$',
                message='Only digits are allowed.'
            )
        ]
    )
    address = models.CharField(max_length=250)
    city = models.CharField(
        choices=CITY_CHOICES,
        max_length=3,
        default='Mu'
    )
    postal_code = models.CharField(max_length=20)
    payment_method = models.CharField(
        choices=PAYMENT_CHOICES,
        max_length=1,
        default='S'
    )

    class Meta:
        verbose_name = 'order details'
        verbose_name_plural = 'order details'

    def __str__(self):
        return f'{self.order} Details'


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='reviews',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name='reviews',
        on_delete=models.CASCADE
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=1000, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)