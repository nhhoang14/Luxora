from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def home_view(request):
    categories = Category.objects.all().order_by('order')  # nếu có field order
    new_products = Product.objects.order_by('-created_at')[:8]  # 8 sản phẩm mới nhất
    return render(request, 'home.html', {
        'categories': categories,
        'new_products': new_products,
    })

def all_products(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'products.html', {
        'title': 'All Products',
        'categories': categories,
        'products': products
    })


def category_products(request, slug):
    category = Category.objects.get(slug=slug)
    products = category.products.all()
    categories = Category.objects.all()
    return render(request, 'products.html', {
        'title': category.name,
        'categories': categories,
        'products': products
    })

def contact(request):
    return render(request, 'contact.html')


def cart(request):
    return render(request, 'cart.html', {'cart': []})