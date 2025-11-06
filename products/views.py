import random
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from itertools import cycle
from .models import Product, Category

def product_list(request, slug=None):
    CATEGORY_ICONS = ["dine_lamp", "wall_lamp", "table_lamp", "scene"]

    categories = list(Category.objects.annotate(product_count=Count('products')))
    icons_iter = cycle(CATEGORY_ICONS)
    categories_with_icons = [(cat, next(icons_iter)) for cat in categories]
    total_products_count = Product.objects.count()

    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = category.products.all()
        title = category.name
    else:
        products = Product.objects.all()
        title = 'All Products'

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        return render(request, 'products/partials/product_grid.html', {'products': products})

    return render(request, 'products/list.html', {
        'title': title,
        'categories_with_icons': categories_with_icons,
        'products': products,
        'sort': sort,
        'total_products_count': total_products_count,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # Lấy 9 sản phẩm ngẫu nhiên (không bao gồm sản phẩm hiện tại)
    all_products = list(Product.objects.exclude(id=product.id))
    related_products = random.sample(all_products, min(9, len(all_products)))

    return render(request, 'products/detail.html', {
        'product': product,
        'related_products': related_products,  
    })
