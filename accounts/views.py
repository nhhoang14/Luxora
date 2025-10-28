from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import RegisterForm, AddressForm
from .models import Address

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Đăng ký thành công!")
            return redirect("addresses_list")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})

@login_required
def addresses_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, "accounts/addresses.html", {"addresses": addresses})

@login_required
def address_form(request, id=None):
    address = get_object_or_404(Address, id=id, user=request.user) if id else None
    form = AddressForm(request.POST or None, instance=address)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        messages.success(request, "Đã lưu địa chỉ.")
        return redirect("addresses_list")
    return render(request, "accounts/address_form.html", {"form": form, "addr": address})

@login_required
def address_delete(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    messages.success(request, "Đã xoá địa chỉ.")
    return redirect("addresses_list")

@login_required
def orders_list(request):
    orders = []
    try:
        from orders.models import Order  # optional
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
    except Exception:
        pass
    return render(request, "accounts/orders.html", {"orders": orders})
