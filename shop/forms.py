from django import forms
from .models import Category, OrderItem

PRODUCT_FILTER_INITIAL = {
    'sort_by': '-created',
    'name__icontains': None,
    'category': None,
    'min_price': None,
    'max_price': None,
    'include_out_of_stock': None,
}

SORT_BY_CHOICES = (
    ('-created', 'Newest First'),
    ('price', 'Price low to high'),
    ('-price', 'Price high to low'),
)

class ProductFilterForm(forms.Form):
    sort_by = forms.ChoiceField(
        choices=SORT_BY_CHOICES,
        required=False
    )
    name__icontains = forms.CharField(
        label='Search',
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
