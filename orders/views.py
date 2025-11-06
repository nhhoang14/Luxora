from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from products.models import Product
from cart.utils import get_cart 
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from accounts.models import Address
from django.db.models import Case, When, Value, IntegerField
from django.urls import reverse

# helper: ordered queryset where cancelled orders are placed last
def get_user_orders_ordered(user):
    return Order.objects.filter(user=user).annotate(
        _is_cancelled=Case(
            When(status='cancelled', then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('_is_cancelled', '-created_at')


@login_required
def order_checkout(request):
    cart = get_cart(request, create_if_missing=False)
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-id')
    return render(request, 'orders/checkout.html', {'cart': cart, 'addresses': addresses})

@login_required
def order_checkout_confirm(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Invalid method"}, status=405)

    cart = get_cart(request, create_if_missing=False)
    if not cart or not cart.items.exists():
        return JsonResponse({
            "success": False,
            "message": "Giỏ hàng trống!",
            "redirect": reverse('cart:cart')
        }, status=400)

    user = request.user

    # Prefer default address
    default_addr = Address.objects.filter(user=user, is_default=True).first()
    if default_addr:
        final_fullname = default_addr.recipient_name
        final_phone = default_addr.phone
        final_address = default_addr.address
    else:
        # fallback: address_id from form (if user explicitly selected/created)
        address_id = request.POST.get('address_id')
        if address_id:
            try:
                addr_obj = Address.objects.get(id=int(address_id), user=user)
                final_fullname = addr_obj.recipient_name
                final_phone = addr_obj.phone
                final_address = addr_obj.address
            except Address.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "message": "Địa chỉ không hợp lệ. Vui lòng thêm địa chỉ giao hàng.",
                    "redirect": reverse('accounts:profile')
                }, status=400)
        else:
            return JsonResponse({
                "success": False,
                "message": "Bạn chưa có địa chỉ giao hàng. Vui lòng thêm địa chỉ.",
                "redirect": reverse('accounts:profile')
            }, status=400)

    # check stock for all items
    insufficient = []
    items = cart.items.select_related('product').all()
    for item in items:
        product = item.product
        qty = item.quantity or 1
        stock = getattr(product, 'stock', None)
        if stock is not None and qty > stock:
            insufficient.append({
                "name": product.name,
                "available": stock,
                "requested": qty
            })

    if insufficient:
        # build readable message
        parts = [f"{i['name']} chỉ còn {i['available']} (yêu cầu {i['requested']})" for i in insufficient]
        return JsonResponse({
            "success": False,
            "message": "Không thể đặt hàng: " + "; ".join(parts),
            "redirect": reverse('cart:cart')
        }, status=400)

    # all ok -> create order, create items, decrement stock, clear cart
    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            full_name=final_fullname,
            phone=final_phone,
            address=final_address,
        )
        for item in items:
            product = item.product
            quantity = item.quantity or 1
            price = getattr(product, 'price', 0)
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
            if getattr(product, 'stock', None) is not None:
                product.stock = max(0, product.stock - quantity)
                product.save(update_fields=['stock'])

        # clear cart
        cart.items.all().delete()
        request.session.pop('cart_id', None)
        request.session.modified = True

    return JsonResponse({
        "success": True,
        "message": "Thanh toán thành công! Đơn đã được lưu.",
        "order_id": order.id,
        "redirect": reverse('accounts:profile')
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/partials/order_detail.html", {"order": order})


@login_required
def order_list(request):
    orders = get_user_orders_ordered(request.user)
    return render(request, 'orders/list.html', {'orders': orders})


@login_required
def cancel_order(request, order_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid method"}, status=405)

    order = get_object_or_404(Order, id=order_id, user=request.user)

    # chỉ cho hủy khi ở trạng thái cho phép
    if getattr(order, "status", None) not in ("pending", "shipping"):
        return JsonResponse({"success": False, "message": "Không thể hủy đơn hàng ở trạng thái này."}, status=400)

    # atomic + select_for_update để tránh race khi cập nhật stock
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)

        # nếu đã hủy trước đó thì không làm gì
        if order.status == "cancelled":
            return JsonResponse({"success": False, "message": "Đơn hàng đã bị hủy trước đó."}, status=400)

        # Trả lại số lượng cho từng sản phẩm (nếu model Product có trường `stock`)
        for item in order.items.select_related("product").all():
            product = item.product
            if product is None:
                continue
            if getattr(product, "stock", None) is not None:
                product.stock = (product.stock or 0) + (item.quantity or 0)
                product.save(update_fields=["stock"])

        order.status = "cancelled"
        order.save(update_fields=["status"])

    # Nếu request từ HTMX, trả partial cập nhật danh sách đơn
    if request.headers.get("HX-Request"):
        orders = get_user_orders_ordered(request.user)
        html = render(request, 'orders/partials/orders_list.html', {'orders': orders}).content.decode('utf-8')
        return HttpResponse(html)

    return JsonResponse({"success": True, "message": "Đã hủy đơn hàng và trả lại tồn kho."})
