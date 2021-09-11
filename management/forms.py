from django import forms
from shop.models import Category, Product, ProductImage, Order

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ('image',)


class OrderRejectForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('reject_reason',)
        widgets = {
            'reject_reason': forms.Textarea(attrs={'rows': 7})
        }