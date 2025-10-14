from django.shortcuts import render

def cart(request):
    return render(request, 'cart.html', {'cart': []})

def cart_tab(request):
    cart = request.session.get('cart', {'items': []})
    return render(request, 'cart/partials/cart_tab.html', {'cart': cart})

def viewed_tab(request):
    viewed_products = request.session.get('viewed_products', [])
    return render(request, 'cart/partials/viewed_tab.html', {'viewed_products': viewed_products})