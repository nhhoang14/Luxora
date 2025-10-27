from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from products.models import Product
from .models import Cart, CartItem
from .utils import get_cart


def cart(request):
    cart = get_cart(request, create_if_missing=True)
    return render(request, 'cart.html', {"cart": cart})


def cart_tab(request):
    cart = get_cart(request, create_if_missing=True)
    return render(request, 'cart/partials/cart_tab.html', {"cart": cart})


def cart_add(request):
    if request.method == "POST":
        product_id = request.POST.get("product")
        color = request.POST.get("color")

        # 🔹 Chuẩn hóa color_id (tránh trường hợp 'None', '', 'null')
        try:
            color_id = int(color) if color and color.lower() not in ["none", "null", ""] else None
        except (ValueError, TypeError, AttributeError):
            color_id = None

        # 🔹 Lấy sản phẩm
        product = get_object_or_404(Product, pk=product_id)
        cart = get_cart(request, create_if_missing=True)

        # 🔹 Lấy số lượng (mặc định = 1)
        try:
            qty = int(request.POST.get("qty", 1))
        except (ValueError, TypeError):
            qty = 1

        # 🔹 Nếu sản phẩm này đã có trong giỏ (cùng color_id), tăng số lượng
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            color_id=color_id,
            defaults={"quantity": qty}
        )

        if not created:
            item.quantity += qty
            item.save()

        # ✅ Cập nhật lại giao diện drawer
        return render(request, "cart/partials/cart_tab.html", {"cart": cart})

    return HttpResponse(status=405)



def remove_from_cart(request):
    if request.method == "POST":
        cart = get_cart(request, create_if_missing=True)
        product_id = request.POST.get("product")
        color = request.POST.get("color")

        try:
            color_id = int(color) if color and color.lower() != "none" else None
        except (ValueError, TypeError, AttributeError):
            color_id = None

        if not product_id or not product_id.isdigit():
            return HttpResponseBadRequest("Invalid product ID")

        qs = CartItem.objects.filter(cart=cart, product_id=int(product_id))
        if color_id is not None:
            qs = qs.filter(color_id=color_id)

        item = qs.first()
        if item:
            item.delete()

        return render(request, "cart/partials/cart_tab.html", {"cart": cart})

    return HttpResponse(status=405)


def cart_update(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    product_id = request.POST.get("product")
    color = request.POST.get("color")

    if not product_id:
        return HttpResponseBadRequest("Missing product")

    try:
        color_id = int(color) if color and color.lower() != "none" else None
    except (ValueError, TypeError, AttributeError):
        color_id = None

    try:
        qty = int(request.POST.get("qty", 1))
    except (ValueError, TypeError):
        qty = 1

    cart = get_cart(request, create_if_missing=True)
    request.session["cart_id"] = cart.id

    qs = CartItem.objects.filter(cart=cart, product_id=product_id)
    if color_id is not None:
        qs = qs.filter(color_id=color_id)

    item = qs.first()

    if qty <= 0:
        if item:
            item.delete()
    else:
        if item:
            item.quantity = qty
            item.save()
        else:
            product = get_object_or_404(Product, pk=product_id)
            CartItem.objects.create(cart=cart, product=product, color_id=color_id, quantity=qty)

    return render(request, "cart/partials/cart_tab.html", {"cart": cart})
