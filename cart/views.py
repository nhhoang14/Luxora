from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from products.models import Product
from .models import Cart, CartItem
from .utils import get_cart

def cart(request):
    return render(request, 'cart.html')


def cart_tab(request):
    return render(request, 'cart/partials/cart_tab.html')

def cart_add(request):
    if request.method == "POST":
        product_id = request.POST.get("product")
        qty = int(request.POST.get("qty", 1))
        product = get_object_or_404(Product, pk=product_id)

        cart = get_cart(request, create_if_missing=True)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += qty
        item.save()

        return render(request, "cart/partials/cart_tab.html", {"cart": cart})

    return HttpResponse(status=405)

def remove_from_cart(request):
    if request.method == "POST":
        cart = get_cart(request, create_if_missing=True)
        product_id = request.POST.get("product")

        if not product_id or not product_id.isdigit():
            return HttpResponse("Invalid product ID", status=400)

        item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
        if item:
            item.delete()

        return render(request, "cart/partials/cart_tab.html", {"cart": cart})

    return HttpResponse(status=405)


def cart_update(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    product_id = request.POST.get("product")
    if not product_id:
        return HttpResponseBadRequest("Missing product")

    try:
        qty = int(request.POST.get("qty", 1))
    except (ValueError, TypeError):
        qty = 1

    cart = get_cart(request, create_if_missing=True)
    if not request.user.is_authenticated:
        request.session["cart_id"] = cart.id

    item = CartItem.objects.filter(cart=cart, product_id=product_id).first()

    if qty <= 0:
        if item:
            item.delete()
    else:
        if item:
            item.quantity = qty
            item.save()
        else:
            product = get_object_or_404(Product, pk=product_id)
            CartItem.objects.create(cart=cart, product=product, quantity=qty)

    return render(request, "cart/partials/cart_tab.html", {"cart": cart})
