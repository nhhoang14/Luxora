# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Danh sách các đơn hàng (hiện có)
    path('', views.order_checkout, name='checkout'),
    path('confirm/', views.order_checkout_confirm, name='checkout_confirm'),
    # Trang chi tiết đơn hàng
    path('<int:order_id>/', views.order_detail, name='detail'),
]
