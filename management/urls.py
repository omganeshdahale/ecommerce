from django.urls import path
from .views import *

app_name = 'management'

urlpatterns = [
    path('categories/', category_list, name='category_list'),
    path('category/create/', category_create, name='category_create'),
    path('category/<int:pk>/edit/', category_edit, name='category_edit'),
    path('category/<int:pk>/delete/', category_delete, name='category_delete'),

    path('products/', product_list, name='product_list'),
    path('product/create/', product_create, name='product_create'),
    path('product/<int:pk>/edit/', product_edit, name='product_edit'),
    path('product/<int:pk>/delete/', product_delete, name='product_delete'),
]
