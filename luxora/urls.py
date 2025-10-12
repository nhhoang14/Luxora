from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Trang chủ
    path('', views.home_view, name='home'),

    # Trang tất cả sản phẩm
    path('products/', views.all_products, name='products'),

    # Trang sản phẩm theo danh mục
    path('category/<slug:slug>/', views.category_products, name='category_products'),

    # Trang liên hệ
    path('contact/', views.contact, name='contact'),

    # Trang giỏ hàng
    path('cart/', views.cart, name='cart'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
