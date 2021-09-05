from django import forms
from .models import (
    Category,
    OrderItem,
    OrderDetails,
    Review,
    PAYMENT_CHOICES
)

PRODUCT_FILTER_INITIAL = {
    'sort_by': '-created',
    'search': None,
    'category': None,
    'min_price': None,
    'max_price': None,
    'min_rating': None,
    'include_out_of_stock': None,
}

SORT_BY_CHOICES = (
    ('-created', 'Newest First'),
    ('price', 'Price low to high'),
    ('-price', 'Price high to low'),
    ('-rating', 'Highest rating'),
)

class ProductFilterForm(forms.Form):
    sort_by = forms.ChoiceField(
        choices=SORT_BY_CHOICES,
        required=False
    )
    search = forms.CharField(
        max_length=100,
        required=False
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label='All',
        required=False,
    )
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    min_rating = forms.IntegerField(
        max_value=5,
        min_value=1,
        required=False
    )
    include_out_of_stock = forms.BooleanField(required=False)


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        initial=1,
        max_value=20,
        min_value=1,
        widget=forms.NumberInput(
            attrs={'class': 'form-control quantity-input'}
        )
    )


class UpdateCartForm(forms.ModelForm):
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={'class': 'form-control d-inline quantity-input'}
        )
    )

    class Meta:
        model = OrderItem
        fields = ['quantity']


class CheckoutForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect()
    )

    class Meta:
        model = OrderDetails
        exclude = ['order']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'rows': 5})
        }