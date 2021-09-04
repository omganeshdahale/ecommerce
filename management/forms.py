from django import forms
from shop.models import Category, Product, ProductImage

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