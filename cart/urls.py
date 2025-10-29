from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart, name='cart'),
    path('cart_tab/', views.cart_tab, name='cart_tab'),

    # unify update/remove -> cart_modify
    path('update/', views.cart_modify, name='update'),
    path('remove/', views.cart_modify, name='remove'),

    path("checkout/", views.cart_checkout, name="checkout"), 
    path("checkout/confirm/", views.cart_checkout_confirm, name="checkout_confirm"),
]