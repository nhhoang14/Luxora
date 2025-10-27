from .models import Cart

def get_cart(request, create_if_missing=False):
    cart = None

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart = Cart.objects.filter(pk=cart_id, user__isnull=True).first()
        if not cart and create_if_missing:
            cart = Cart.objects.create()
            request.session["cart_id"] = cart.id

    return cart
