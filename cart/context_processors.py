from .utils import get_cart

def cart_context(request):
    try:
        cart = get_cart(request)
    except Exception:
        cart = None
    return {'cart': cart}
