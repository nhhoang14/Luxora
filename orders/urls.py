# orders/urls.py
from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    # Danh sách các đơn hàng (hiện có)
    path('', views.order_checkout, name='checkout'),
    path('confirm/', views.order_checkout_confirm, name='checkout_confirm'),
    # Trang chi tiết đơn hàng
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    # Hủy đơn
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    # Danh sách người dùng xem các đơn hàng của họ
    path('list/', views.order_list, name='list'),
]
