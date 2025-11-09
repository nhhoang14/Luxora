from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from products.models import Category, Product
from .models import ContactMessage

def home_view(request):
    categories = Category.objects.all().order_by('order')
    new_products = Product.objects.order_by('-created_at')[:10]  # lấy 10 sản phẩm mới nhất
    return render(request, 'home.html', {
        'categories': categories,
        'new_products': new_products,
    })

def contact_view(request):
    return render(request, 'contact.html')

def contact_submit(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        # lưu vào DB
        ContactMessage.objects.create(name=name, email=email, message=message)
        res = HttpResponse('', status=204)
        res['HX-Trigger'] = 'contactSuccess'
        return res
    return HttpResponse("<p class='text-red-600 font-medium'>Vui lòng gửi lại!</p>")

def nav_category_products(request, slug):
    category = get_object_or_404(Category.objects.prefetch_related('products'), slug=slug)
    products = category.products.all()[:3]
    return render(request, 'products/partials/category_products.html', {
        'category': category,
        'products': products,
    })