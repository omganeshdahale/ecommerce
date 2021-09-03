from django.urls import path
from .views import *

app_name = 'management'

urlpatterns = [
    path('categories/', category_list, name='category_list'),
    path('category/create/', category_create, name='category_create'),
    path('category/<int:pk>/edit/', category_edit, name='category_edit'),
    path('category/<int:pk>/delete/', category_delete, name='category_delete'),
]
