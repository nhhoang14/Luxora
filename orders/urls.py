# orders/urls.py
from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path('', views.order_checkout, name='checkout'),
    path('confirm/', views.order_checkout_confirm, name='checkout_confirm'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('list/', views.order_list, name='list'),
]
