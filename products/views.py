from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'products/list.html', {
        'title': 'All Products',
        'categories': categories,
        'products': products,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    viewed_products = request.session.get('viewed_products', [])
    if product.id not in [p['id'] for p in viewed_products]:
        viewed_products.insert(0, {
            'id': product.id,
            'name': product.name,
            'image': str(product.image),
            'price': float(product.price)
        })
        viewed_products = viewed_products[:10]
        request.session['viewed_products'] = viewed_products

    return render(request, 'products/detail.html', {'product': product})

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    categories = Category.objects.all()
    return render(request, 'products/list.html', {
        'title': category.name,
        'categories': categories,
        'products': products
    })