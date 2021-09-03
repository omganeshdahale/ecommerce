from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Category
from .decorators import group_required
from .forms import CategoryForm

@login_required
@group_required('admin')
def category_list(request):
    return render(request, 'management/category_list.html', {
        'categories': Category.objects.all()
    })

@login_required
@group_required('admin')
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')

            return redirect('management:category_list')
    else:
        form = CategoryForm()

    return render(request, 'management/category_create.html', {'form': form})

@login_required
@group_required('admin')
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category saved successfully.')

            return redirect('management:category_edit', pk=pk)
    else:
        form = CategoryForm(instance=category)

    context = {
        'category': category,
        'form': form
    }
    return render(request, 'management/category_edit.html', context)

@require_POST
@login_required
@group_required('admin')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully.')

    return redirect('management:category_list')