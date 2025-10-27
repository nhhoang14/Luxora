# products/views.py

from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Color
import random


# ✅ Trang tất cả sản phẩm
def product_list(request):
    categories = Category.objects.all()
    colors = Color.objects.all()

    selected_color_id = request.GET.get('color')
    products = Product.objects.all()

    if selected_color_id:
        products = products.filter(colors__id=selected_color_id)

    # Banner mặc định
    banner_image = 'images/banner-products.jpg'

    return render(request, 'products/list.html', {
        'title': 'Tất cả sản phẩm',
        'categories': categories,
        'colors': colors,
        'products': products.distinct(),
        'selected_category': None,
        'selected_color_id': int(selected_color_id) if selected_color_id else None,
        'banner_image': banner_image,
    })


# ✅ Trang lọc theo danh mục
def category_products(request, slug):
    categories = Category.objects.all()
    colors = Color.objects.all()
    category = get_object_or_404(Category, slug=slug)

    selected_color_id = request.GET.get('color')

    products = Product.objects.filter(categories=category)
    if selected_color_id:
        products = products.filter(colors__id=selected_color_id)

    # Banner riêng theo từng danh mục
    banner_image = category.get_image()  # tự trả về banner đúng slug hoặc ảnh mặc định

    return render(request, 'products/list.html', {
        'title': category.name,
        'categories': categories,
        'colors': colors,
        'products': products.distinct(),
        'selected_category': category,
        'selected_color_id': int(selected_color_id) if selected_color_id else None,
        'banner_image': banner_image,
    })


# ✅ Trang chi tiết sản phẩm
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # --- Thường mua kèm: chọn ngẫu nhiên 3 sản phẩm khác ---
    all_products = list(Product.objects.exclude(id=product.id))
    recommended_products = random.sample(all_products, min(3, len(all_products)))

    # --- Ghi nhớ sản phẩm đã xem (tối đa 10 sản phẩm) ---
    viewed_products = request.session.get('viewed_products', [])
    if product.id not in [p['id'] for p in viewed_products]:
        viewed_products.insert(0, {
            'id': product.id,
            'name': product.name,
            'image': str(product.image),
            'price': float(product.price),
        })
        viewed_products = viewed_products[:10]
        request.session['viewed_products'] = viewed_products

    # --- Lấy danh mục & màu để hiển thị ở menu ---
    categories = Category.objects.all()
    colors = Color.objects.all()

    # --- Danh sách gợi ý thêm nếu cần ---
    products = Product.objects.exclude(id=product.id)[:8]

    # --- Render template ---
    return render(request, 'products/detail.html', {
        'product': product,
        'recommended_products': recommended_products,
        'categories': categories,
        'colors': colors,
        'products': products,
    })
