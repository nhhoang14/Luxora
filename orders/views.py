from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Order, OrderItem
from products.models import Product
from cart.utils import get_cart  # dùng hàm get_cart của app cart

@login_required
def order_checkout(request):
    """
    GET: hiển thị form checkout (lấy cart từ get_cart)
    """
    cart = get_cart(request, create_if_missing=False)

    # nếu không có cart hoặc rỗng -> quay về trang giỏ hàng
    if not cart or not getattr(cart, "items", None) or not cart.items.exists():
        messages.warning(request, "Giỏ hàng của bạn đang trống!")
        return redirect('cart:cart')

    # Only GET here; POST handled by order_checkout_confirm
    return render(request, 'orders/checkout.html', {'cart': cart})


@login_required
def order_checkout_confirm(request):
    """
    Xử lý POST xác nhận thanh toán (AJAX). Trả JSON.
    """
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Invalid method"}, status=405)

    cart = get_cart(request, create_if_missing=False)
    if not cart or not getattr(cart, "items", None) or not cart.items.exists():
        return JsonResponse({"success": False, "message": "Giỏ hàng trống"}, status=400)

    full_name = request.POST.get('fullname') or request.POST.get('full_name')
    phone = request.POST.get('phone')
    address = request.POST.get('address')
    payment_method = request.POST.get('payment_method', 'cod')

    # validate basic fields
    if not full_name or not phone or not address:
        return JsonResponse({"success": False, "message": "Vui lòng nhập đầy đủ thông tin giao hàng"}, status=400)

    # Tạo Order + OrderItem
    order = Order.objects.create(
        user=request.user,
        full_name=full_name,
        phone=phone,
        address=address,
        payment_method=payment_method,
    )

    for item in cart.items.all():
        product = item.product
        quantity = item.quantity or 1
        price = getattr(product, 'price', 0)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price
        )

    # Xóa items trong cart và session
    cart.items.all().delete()
    request.session.pop('cart_id', None)
    request.session.modified = True

    return JsonResponse({
        "success": True,
        "message": "Thanh toán thành công! Cảm ơn bạn. Đang chuyển về trang chủ...",
        "order_id": order.id
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/list.html', {'orders': orders})
