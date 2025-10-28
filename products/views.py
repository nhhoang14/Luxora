from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def product_list(request, slug=None):
    categories = Category.objects.all()
    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = category.products.all()
        title = category.name
    else:
        products = Product.objects.all()
        title = 'All Products'

    # HTMX: chỉ trả partial grid
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        return render(request, 'products/partials/product_grid.html', {
            'products': products,
        })

    return render(request, 'products/list.html', {
        'title': title,
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
        request.session['viewed_products'] = viewed_products[:10]

    return render(request, 'products/detail.html', {'product': product})