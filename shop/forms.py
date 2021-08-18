from django import forms
from .models import Category

SORT_BY_CHOICES = (
    ('created', 'Newest First'),
    ('price', 'Price low to high'),
    ('-price', 'Price high to low'),
)

class ProductFilterForm(forms.Form):
    sort_by = forms.ChoiceField(
        choices=SORT_BY_CHOICES,
        initial='created',
        required=False
    )
    name__icontains = forms.CharField(
        label='Search',
        max_length=100,
        required=False
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        to_field_name='name',
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
