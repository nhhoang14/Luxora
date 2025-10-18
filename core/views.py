from django.shortcuts import render, get_object_or_404
from products.models import Category, Product

def home_view(request):
    categories = Category.objects.all().order_by('order')  # nếu có field order
    new_products = Product.objects.order_by('-created_at')[:8]  # 8 sản phẩm mới nhất
    return render(request, 'home.html', {
        'categories': categories,
        'new_products': new_products,
    })

def contact_view(request):
    return render(request, 'contact.html')

def quick_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'partials/quickview_modal.html', {'product': product})

def nav_category_products(request, slug):
    category = get_object_or_404(Category.objects.prefetch_related('products'), slug=slug)
    products = category.products.all()[:3]
    return render(request, 'products/partials/category_products.html', {
        'category': category,
        'products': products,
    })