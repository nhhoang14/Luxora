from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from products.models import Product
from .models import CartItem
from .utils import get_cart
from django.http import JsonResponse


# 🛒 Trang giỏ hàng chính
def cart(request):
    cart_obj = get_cart(request, create_if_missing=True)
    return render(request, 'cart/cart.html', {"cart": cart_obj})


# 🧩 Tab giỏ hàng mini (HTMX)
def cart_tab(request):
    cart_obj = get_cart(request, create_if_missing=True)
    return render(request, 'cart/partials/cart_tab.html', {"cart": cart_obj})


# ➕ Thêm sản phẩm vào giỏ
# ➕ Thêm sản phẩm vào giỏ
def cart_add(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    # 🔹 Lấy thông tin sản phẩm
    product_id = request.POST.get("product")

    # 🔹 Lấy số lượng (mặc định = 1)
    try:
        qty = int(request.POST.get("qty", 1))
    except (ValueError, TypeError):
        qty = 1

    # 🔹 Lấy sản phẩm và giỏ hàng
    product = get_object_or_404(Product, pk=product_id)
    cart_obj = get_cart(request, create_if_missing=True)

    # 🔹 Tạo hoặc cập nhật sản phẩm trong giỏ
    item, created = CartItem.objects.get_or_create(cart=cart_obj, product=product)
    if not created:
        item.quantity += qty
    else:
        item.quantity = qty
    item.save()

    # ✅ Trả về giao diện
    if request.headers.get("HX-Request"):
        return render(request, "cart/partials/cart_tab.html", {"cart": cart_obj})

    return render(request, "cart/cart.html", {"cart": cart_obj})


# ❌ Xóa sản phẩm
def cart_remove(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    cart_obj = get_cart(request, create_if_missing=True)

    product_id = request.POST.get("product")
    item_id = request.POST.get("item_id")

    if product_id and product_id.isdigit():
        item = CartItem.objects.filter(cart=cart_obj, product_id=product_id).first()
    elif item_id and item_id.isdigit():
        item = CartItem.objects.filter(cart=cart_obj, id=item_id).first()
    else:
        return HttpResponse("Invalid item", status=400)

    if item:
        item.delete()
    return render(request, "cart/cart.html", {"cart": cart_obj})

def cart_tab_remove(request):
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

# 🔁 Cập nhật số lượng
def cart_update(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    product_id = request.POST.get("product")
    if not product_id:
        return HttpResponseBadRequest("Missing product")

    try:
        qty = int(request.POST.get("qty", 1))
    except (ValueError, TypeError):
        qty = 1

    cart_obj = get_cart(request, create_if_missing=True)
    if not request.user.is_authenticated:
        request.session["cart_id"] = cart_obj.id

    item = CartItem.objects.filter(cart=cart_obj, product_id=product_id).first()

    if qty <= 0:
        if item:
            item.delete()
            return HttpResponse("")  # xóa item → trả về rỗng cho HTMX
    else:
        if item:
            item.quantity = qty
            item.save()
        else:
            product = get_object_or_404(Product, pk=product_id)
            item = CartItem.objects.create(cart=cart_obj, product=product, quantity=qty)

    return render(request, "cart/cart.html", {"cart": cart_obj})



def cart_tab_update(request):
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

# 🧾 Trang thanh toán (checkout)
def cart_checkout(request):
    cart_obj = get_cart(request, create_if_missing=True)

    if not cart_obj.items.exists():
        messages.error(request, "Giỏ hàng của bạn đang trống.")
        return redirect("cart:cart")

    return render(request, "cart/cart_checkout.html", {"cart": cart_obj})


def cart_checkout_confirm(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "❌ Phương thức không hợp lệ."}, status=405)

    cart = get_cart(request, create_if_missing=True)
    payment = request.POST.get("payment_method")

    # Kiểm tra giỏ hàng
    if not cart.items.exists():
        return JsonResponse({"success": False, "message": "🛒 Giỏ hàng của bạn đang trống."})

    # Kiểm tra phương thức thanh toán
    if payment not in ["cash", "qr"]:
        return JsonResponse({"success": False, "message": "⚠️ Vui lòng chọn phương thức thanh toán hợp lệ."})

    # Xử lý thanh toán
    messages = {
        "cash": "💵 Đơn hàng đã được xác nhận! Thanh toán khi nhận hàng.",
        "qr": "✅ Thanh toán qua mã QR thành công! Cảm ơn bạn đã mua hàng."
    }

    # Xóa giỏ hàng sau khi thanh toán
    cart.items.all().delete()

    return JsonResponse({"success": True, "message": messages[payment]})