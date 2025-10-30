from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from products.models import Product


@login_required
def checkout(request):
    """
    Xử lý khi người dùng nhấn 'Check out':
    - Lấy giỏ hàng từ session
    - Tạo Order và OrderItem
    - Xóa giỏ hàng sau khi tạo đơn thành công
    """
    cart = request.session.get('cart', {})  # Giỏ hàng lưu trong session

    if not cart:
        messages.warning(request, "Giỏ hàng của bạn đang trống!")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method', 'cod')

        # Tạo đơn hàng
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            payment_method=payment_method,
        )

        # Tạo các dòng chi tiết đơn hàng (OrderItem)
        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id)
            quantity = item.get('quantity', 1)
            price = product.price
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )

        # Sau khi tạo đơn hàng → xóa giỏ hàng
        request.session['cart'] = {}
        messages.success(request, "Đơn hàng của bạn đã được tạo thành công!")
        return redirect('orders:order_detail', order_id=order.id)

    return render(request, 'orders/checkout.html')


@login_required
def order_detail(request, order_id):
    """
    Hiển thị chi tiết 1 đơn hàng cụ thể.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})


@login_required
def order_list(request):
    """
    Hiển thị danh sách các đơn hàng của người dùng.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/list.html', {'orders': orders})
