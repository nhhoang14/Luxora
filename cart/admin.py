from django.contrib import admin
from .models import Cart, CartItem, ViewedProduct
    
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(ViewedProduct)
