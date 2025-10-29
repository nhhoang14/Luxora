from .models import Cart

def get_cart(request, create_if_missing=False):
    cart = None

    # Nếu user đã đăng nhập
    if request.user.is_authenticated:
        # Nếu session có giỏ tạm (tạo trước khi đăng nhập)
        session_cart_id = request.session.get("cart_id")
        session_cart = None
        if session_cart_id:
            session_cart = Cart.objects.filter(pk=session_cart_id, user__isnull=True).first()

        # Lấy hoặc tạo giỏ cho user
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Nếu có giỏ session trước đó → gộp vào giỏ user
        if session_cart and session_cart != cart:
            for item in session_cart.items.all():
                existing_item = cart.items.filter(product=item.product).first()
                if existing_item:
                    existing_item.quantity += item.quantity
                    existing_item.save()
                else:
                    item.cart = cart
                    item.save()
            session_cart.delete()
            request.session.pop("cart_id", None)

        return cart

    # Nếu chưa đăng nhập → lấy từ session
    cart_id = request.session.get("cart_id")
    if cart_id:
        cart = Cart.objects.filter(pk=cart_id, user__isnull=True).first()

    # Nếu chưa có giỏ và được phép tạo mới
    if not cart and create_if_missing:
        cart = Cart.objects.create()
        request.session["cart_id"] = cart.id

    return cart
