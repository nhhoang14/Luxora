# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Danh sách các đơn hàng (hiện có)
    path('', views.order_list, name='list'),

    # Trang thanh toán / đặt hàng
    path('checkout/', views.checkout, name='checkout'),

    # Trang chi tiết đơn hàng
    path('<int:order_id>/', views.order_detail, name='detail'),
]
