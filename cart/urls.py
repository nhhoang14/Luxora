from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart, name='cart'),
    path('cart_tab/', views.cart_tab, name='cart_tab'),
    path("modify/", views.cart_modify, name="modify"),
    path("checkout/", views.cart_checkout, name="checkout"), 
    path("checkout/confirm/", views.cart_checkout_confirm, name="checkout_confirm"),
]