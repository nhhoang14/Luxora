import random
from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def product_list(request, slug=None):
    categories = Category.objects.all()
    sort = request.GET.get('sort')  # Lấy giá trị sắp xếp từ query string (price_asc / price_desc)

    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = category.products.all()
        title = category.name
    else:
        products = Product.objects.all()
        title = 'All Products'

    # Áp dụng sắp xếp
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    # HTMX: chỉ trả partial grid
    if request.headers.get('HX-Request') or request.META.get('HTTP_HX_REQUEST'):
        return render(request, 'products/partials/product_grid.html', {
            'products': products,
        })

    return render(request, 'products/list.html', {
        'title': title,
        'categories': categories,
        'products': products,
        'sort': sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # Lưu lịch sử xem
    viewed_products = request.session.get('viewed_products', [])
    if product.id not in [p['id'] for p in viewed_products]:
        viewed_products.insert(0, {
            'id': product.id,
            'name': product.name,
            'image': str(product.image),
            'price': float(product.price)
        })
        request.session['viewed_products'] = viewed_products[:10]

    # ✅ Lấy 9 sản phẩm ngẫu nhiên (không bao gồm sản phẩm hiện tại)
    all_products = list(Product.objects.exclude(id=product.id))
    related_products = random.sample(all_products, min(9, len(all_products)))

    return render(request, 'products/detail.html', {
        'product': product,
        'related_products': related_products,  # ✅ truyền vào template
    })
