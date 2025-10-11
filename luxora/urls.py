from django.contrib import admin
from django.urls import path
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: render(request, 'index.html'), name='home'),
    path('products/', lambda request: render(request, 'products.html', {'products': []}), name='products'),
    path('contact/', lambda request: render(request, 'contact.html'), name='contact'),
    path('cart/', lambda request: render(request, 'cart.html', {'cart': []}), name='cart'),
]
