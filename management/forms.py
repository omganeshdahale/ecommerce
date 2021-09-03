from django import forms
from shop.models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']