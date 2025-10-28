from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/",  auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", views.register, name="register"),

    path("password/change/", auth_views.PasswordChangeView.as_view(
        template_name="accounts/password_change_form.html",
        success_url="/password/change/done/"
    ), name="password_change"),
    path("password/change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="accounts/password_change_done.html"
    ), name="password_change_done"),

    path("addresses/", views.addresses_list, name="addresses_list"),
    path("addresses/new/", views.address_form, name="address_new"),
    path("addresses/<int:id>/edit/", views.address_form, name="address_edit"),
    path("addresses/<int:id>/delete/", views.address_delete, name="address_delete"),

    path("orders/", views.orders_list, name="orders_list"),
]
