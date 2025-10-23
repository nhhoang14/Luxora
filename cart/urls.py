from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart, name='cart'),
    path('cart_tab/', views.cart_tab, name='cart_tab'),
    path("add/", views.cart_add, name="add"),
    path('update/', views.cart_update, name='update'),
    path('remove/', views.remove_from_cart, name='remove'),
]