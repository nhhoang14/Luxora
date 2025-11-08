from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.login_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('password-change/', views.change_password_view, name='change_password'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/<int:address_id>/edit/', views.edit_address, name='edit_address'),
    path('address/<int:address_id>/delete/', views.delete_address, name='delete_address'),
    path('address/<int:address_id>/set-default/', views.set_default_address, name='set_default_address'),
]
