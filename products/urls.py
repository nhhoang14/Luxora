from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'), 
    path('category/<slug:slug>/', views.product_list, name='category'),
    path('<slug:slug>/', views.product_detail, name='detail'), 
]