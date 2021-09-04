from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import modelformset_factory, inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Category, Product, ProductImage
from .decorators import group_required
from .forms import CategoryForm, ProductForm, ProductImageForm

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

@login_required
@group_required('admin')
def product_list(request):
    paginator = Paginator(Product.objects.all(), 15)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'management/product_list.html', {
        'products': products
    })

@login_required
@group_required('admin')
def product_create(request):
    ProductImageFormSet = modelformset_factory(
        ProductImage,
        form=ProductImageForm,
        extra=3
    )
    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(
            request.POST,
            request.FILES,
            queryset=ProductImage.objects.none()
        )
        if form.is_valid() and formset.is_valid():
            product = form.save()
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    ProductImage(product=product, image=image).save()

            messages.success(request, 'Product created successfully.')

            return redirect('management:product_list')
    else:
        form = ProductForm()
        formset = ProductImageFormSet(queryset=ProductImage.objects.none())

    context = {
        'form': form,
        'formset': formset
    }
    return render(request, 'management/product_create.html', context)

@login_required
@group_required('admin')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    ProductImageFormSet = inlineformset_factory(
        Product,
        ProductImage,
        form=ProductImageForm,
        extra=1
    )
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Product saved successfully.')

            return redirect('management:product_edit', pk=pk)
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)

    context = {
        'product': product,
        'form': form,
        'formset': formset
    }
    return render(request, 'management/product_edit.html', context)

@require_POST
@login_required
@group_required('admin')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Product deleted successfully.')

    return redirect('management:product_list')