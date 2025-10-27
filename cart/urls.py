from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart, name='cart'),
    path('cart_tab/', views.cart_tab, name='cart_tab'),
    path("add/", views.cart_add, name="add"),
    path('update/', views.cart_update, name='update'),
    path('cart/update/', views.cart_tab_update, name='cart_tab_update'),
    path('remove/', views.cart_remove, name='remove'),
    path('cart/remove/', views.cart_tab_remove, name='cart_tab_remove'),
    path("checkout/", views.cart_checkout, name="checkout"), 
    path("checkout/confirm/", views.cart_checkout_confirm, name="checkout_confirm"),
]