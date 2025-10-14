from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart, name='cart'),
    path('cart_tab/', views.cart_tab, name='cart_tab'),
    path('viewed_tab/', views.viewed_tab, name='viewed_tab'),
]