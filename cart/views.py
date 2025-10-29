from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from products.models import Product
from .models import CartItem
from .utils import get_cart
from django.http import JsonResponse


# Trang giỏ hàng chính
def cart(request):
    cart_obj = get_cart(request, create_if_missing=True)
    return render(request, 'cart/cart.html', {"cart": cart_obj})


# Tab giỏ hàng mini (HTMX)
def cart_tab(request):
    cart_obj = get_cart(request, create_if_missing=True)
    return render(request, 'cart/partials/cart_tab.html', {"cart": cart_obj})

# Trang thanh toán (checkout)
def cart_checkout(request):
    cart_obj = get_cart(request, create_if_missing=True)

    if not cart_obj.items.exists():
        messages.error(request, "Giỏ hàng của bạn đang trống.")
        return redirect("cart:cart")

    return render(request, "cart/cart_checkout.html", {"cart": cart_obj})

def cart_modify(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    product_id = request.POST.get("product")
    item_id = request.POST.get("item_id")
    action = request.POST.get("action")
    qty_raw = request.POST.get("qty")

    # parse qty
    try:
        qty = int(qty_raw) if qty_raw is not None else None
    except (ValueError, TypeError):
        qty = None

    cart = get_cart(request, create_if_missing=True)
    if not request.user.is_authenticated and cart:
        request.session["cart_id"] = cart.id

    # find item
    item = None
    if item_id and item_id.isdigit():
        item = CartItem.objects.filter(cart=cart, id=item_id).first()
    elif product_id and product_id.isdigit():
        item = CartItem.objects.filter(cart=cart, product_id=product_id).first()

    # remove if requested or qty <= 0
    if action == "remove" or (qty is not None and qty <= 0):
        if item:
            item.delete()
        # HTMX -> return partial cart tab, else full cart
        if request.headers.get("HX-Request"):
            return render(request, "cart/partials/cart_tab.html", {"cart": cart})
        return render(request, "cart/cart.html", {"cart": cart})

    # update / create
    if qty is None:
        qty = 1
    if item:
        if action == "add":
            item.quantity = (item.quantity or 0) + qty
        else:
            item.quantity = qty
        item.save()
    else:
        product = get_object_or_404(Product, pk=product_id)
        CartItem.objects.create(cart=cart, product=product, quantity=qty)

    if request.headers.get("HX-Request"):
        return render(request, "cart/partials/cart_tab.html", {"cart": cart})
    return render(request, "cart/cart.html", {"cart": cart})

def cart_checkout_confirm(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Phương thức không hợp lệ."}, status=405)

    cart = get_cart(request, create_if_missing=True)
    payment = request.POST.get("payment_method")

    # Kiểm tra giỏ hàng
    if not cart.items.exists():
        return JsonResponse({"success": False, "message": "Giỏ hàng của bạn đang trống."})

    # Kiểm tra phương thức thanh toán
    if payment not in ["cash", "qr"]:
        return JsonResponse({"success": False, "message": "Vui lòng chọn phương thức thanh toán hợp lệ."})

    # Xử lý thanh toán
    messages = {
        "cash": "Đơn hàng đã được xác nhận! Thanh toán khi nhận hàng.",
        "qr": "Thanh toán qua mã QR thành công! Cảm ơn bạn đã mua hàng."
    }

    # Xóa giỏ hàng sau khi thanh toán
    cart.items.all().delete()

    return JsonResponse({"success": True, "message": messages[payment]})