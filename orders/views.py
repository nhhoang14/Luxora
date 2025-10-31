from pyexpat.errors import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from products.models import Product
from cart.utils import get_cart  # dùng hàm get_cart của app cart
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from accounts.models import Address
from django.db.models import Case, When, Value, IntegerField

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
    Hỗ trợ:
     - Nếu user đăng nhập và có địa chỉ mặc định -> luôn dùng địa chỉ mặc định
     - Nếu user đăng nhập và không có mặc định -> fallback sang address_id / new address / default logic cũ
     - Nếu user không đăng nhập -> fullname/phone/address bắt buộc
    """
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Invalid method"}, status=405)

    cart = get_cart(request, create_if_missing=False)
    if not cart or not getattr(cart, "items", None) or not cart.items.exists():
        return JsonResponse({"success": False, "message": "Giỏ hàng trống"}, status=400)

    user = request.user if request.user.is_authenticated else None

    # priority: address_id radio / provided fields (kept for fallback if no default)
    address_id = request.POST.get('address_id')
    full_name = request.POST.get('fullname') or request.POST.get('full_name')
    phone = request.POST.get('phone')
    address_text = request.POST.get('address')
    save_address = request.POST.get('save_address') in ('1', 'on', 'true')
    make_default = request.POST.get('is_default') in ('1', 'on', 'true')

    # determine final full_name/phone/address
    if user:
        # ALWAYS prefer default address if available
        default_addr = Address.objects.filter(user=user, is_default=True).first()
        if default_addr:
            final_fullname = default_addr.recipient_name
            final_phone = default_addr.phone
            final_address = default_addr.address
        else:
            # fallback to previous behaviour
            if address_id:
                try:
                    addr_obj = Address.objects.get(id=int(address_id), user=user)
                    final_fullname = addr_obj.recipient_name
                    final_phone = addr_obj.phone
                    final_address = addr_obj.address
                except Address.DoesNotExist:
                    return JsonResponse({"success": False, "message": "Địa chỉ không hợp lệ"}, status=400)
            elif full_name and phone and address_text:
                final_fullname = full_name.strip()
                final_phone = phone.strip()
                final_address = address_text.strip()

                if save_address:
                    # only save when user has less than 3 addresses
                    if user.addresses.count() < 3:
                        addr = Address(user=user, recipient_name=final_fullname, phone=final_phone, address=final_address, is_default=make_default)
                        try:
                            addr.full_clean()
                            addr.save()
                        except Exception:
                            pass
            else:
                # no address provided and no default -> error
                return JsonResponse({"success": False, "message": "Vui lòng chọn hoặc thêm địa chỉ giao hàng."}, status=400)
    else:
        # guest checkout: require fullname/phone/address_text
        if not (full_name and phone and address_text):
            return JsonResponse({"success": False, "message": "Vui lòng nhập đầy đủ thông tin giao hàng"}, status=400)
        final_fullname = full_name.strip()
        final_phone = phone.strip()
        final_address = address_text.strip()

    # create order and items
    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            full_name=final_fullname,
            phone=final_phone,
            address=final_address,
        )
        for item in cart.items.all():
            product = item.product
            quantity = item.quantity or 1
            price = getattr(product, 'price', 0)
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)

        # clear cart
        cart.items.all().delete()
        request.session.pop('cart_id', None)
        request.session.modified = True

    return JsonResponse({
        "success": True,
        "message": "Thanh toán thành công! Đơn đã được lưu.",
        "order_id": order.id
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
    if getattr(order, "status", None) in ("pending", "shipping", "processing"):
        order.status = "cancelled"
        order.save()
        # after cancel, return updated orders list fragment so client can replace it
        orders = get_user_orders_ordered(request.user)
        html = render(request, 'orders/partials/orders_list.html', {'orders': orders}).content
        return HttpResponse(html)
    return JsonResponse({"success": False, "message": "Không thể hủy đơn hàng ở trạng thái này."}, status=400)
