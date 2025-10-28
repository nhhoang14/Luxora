from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    # Trang admin
    path('admin/', admin.site.urls),

    # Trang chủ & các trang chung
    path('', core_views.home_view, name='home'),
    path("contact/", core_views.contact_view, name="contact"),
    path("contact/submit/", core_views.contact_submit, name="contact_submit"),

    # Navbar
    path('nav/category/<slug:slug>/', core_views.nav_category_products, name='nav_category_products'),

    # Ứng dụng con
    path('products/', include(('products.urls', 'products'), namespace='products')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
]

# Cấu hình hiển thị ảnh & media trong môi trường DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
