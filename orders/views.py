from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from products.models import Product
from cart.utils import get_cart 
from django.db import transaction
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
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
        return HttpResponse('<p class="text-sm font-medium text-red-600">Invalid method</p>', status=405)

    cart = get_cart(request, create_if_missing=False)
    if not cart or not cart.items.exists():
        resp = HttpResponse('<p class="text-sm font-medium text-red-600">Giỏ hàng trống!</p>')
        resp['HX-Redirect'] = reverse('cart:cart')
        return resp

    user = request.user

    # lấy address (cứ giữ logic cũ y chang, chỉ đổi return)
    default_addr = Address.objects.filter(user=user, is_default=True).first()
    if not default_addr:
        address_id = request.POST.get("address_id")
        if not address_id:
            resp = HttpResponse('<p class="text-sm font-medium text-red-600">Bạn chưa có địa chỉ giao hàng.</p>')
            resp['HX-Redirect'] = reverse('accounts:profile')
            return resp
        try:
            default_addr = Address.objects.get(id=address_id, user=user)
        except:
            resp = HttpResponse('<p class="text-sm font-medium text-red-600">Địa chỉ không hợp lệ.</p>')
            resp['HX-Redirect'] = reverse('accounts:profile')
            return resp

    # check stock
    insufficient = []
    for item in cart.items.select_related('product').all():
        if item.product.stock is not None and item.quantity > item.product.stock:
            insufficient.append(f"{item.product.name} chỉ còn {item.product.stock}")

    if insufficient:
        resp = HttpResponse(f'<p class="text-sm font-medium text-red-600">{"; ".join(insufficient)}</p>')
        resp['HX-Redirect'] = reverse('cart:cart')
        return resp

    # create order
    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            full_name=default_addr.recipient_name,
            phone=default_addr.phone,
            address=default_addr.address
        )

        for item in cart.items.all():
            OrderItem.objects.create(order=order, product=item.product,
                                     quantity=item.quantity, price=item.product.price)
            if item.product.stock is not None:
                item.product.stock -= item.quantity
                item.product.save(update_fields=['stock'])

        cart.items.all().delete()
        request.session.pop('cart_id', None)

    resp = HttpResponse('<p class="text-sm font-medium text-green-600">Thanh toán thành công!</p>')
    resp['HX-Redirect'] = reverse('accounts:profile')
    return resp


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
