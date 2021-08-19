from django.urls import path
from .views import *

app_name = 'shop'

urlpatterns = [
    path('', home, name='home'),
    path('shop/', product_list, name='product_list'),
    path('<slug:slug>/', product_detail, name='product_detail'),
]
