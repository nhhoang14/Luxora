from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotAllowed
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .models import Address
from .forms import CustomPasswordChangeForm 

try:
    from orders.models import Order
except Exception:
    Order = None

User = get_user_model()

# ĐĂNG NHẬP
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Chào mừng {user.username} quay lại!")
            return redirect('home')  # trang chủ sau khi đăng nhập
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu!")

    return render(request, 'accounts/partials/login.html')


# ĐĂNG KÝ
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Mật khẩu không khớp!")
            return redirect('accounts:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại!")
            return redirect('accounts:register')

        # tạo tài khoản
        user = User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Tạo tài khoản thành công! Vui lòng đăng nhập.")
        return redirect('accounts:login')

    return render(request, 'accounts/partials/register.html')


# ĐĂNG XUẤT
def logout_view(request):
    logout(request)
    messages.info(request, "Bạn đã đăng xuất.")
    return redirect('home')


# HỒ SƠ NGƯỜI DÙNG
@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user).order_by("-id")
    orders = Order.objects.filter(user=request.user).order_by("-created_at") if Order else []
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'addresses': addresses,
        'orders': orders,
    })


# ĐỔI MẬT KHẨU
@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # giữ đăng nhập
            messages.success(request, "Đổi mật khẩu thành công!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Có lỗi xảy ra, vui lòng thử lại.")
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/partials/change_password.html', {'form': form})


# QUÊN MẬT KHẨU (demo đơn giản)
def password_reset_view(request):
    return HttpResponse("Trang reset mật khẩu đang phát triển.")


# ĐỊNH DẠNG ĐỊA CHỈ
@login_required
def add_address(request):
    if request.method == "GET":
        return render(request, "accounts/partials/address_form.html", {"address": None})

    if request.method == "POST":
        recipient = request.POST.get("recipient_name", "").strip()
        addr = request.POST.get("address", "").strip()
        phone = request.POST.get("phone", "").strip()
        # duplicate check
        dup_qs = Address.objects.filter(
            user=request.user,
            recipient_name__iexact=recipient,
            address__iexact=addr,
            phone__iexact=phone
        )
        if dup_qs.exists():
            # trả form với address=None và lỗi (không trả unsaved instance)
            html = render_to_string("accounts/partials/address_form.html", {
                "address": None,
                "errors": ["Địa chỉ đã tồn tại."],
            }, request=request)
            return HttpResponse(html, status=400)

        address_obj = Address(user=request.user, recipient_name=recipient, address=addr, phone=phone)
        try:
            address_obj.full_clean()
            address_obj.save()
        except ValidationError as e:
            html = render_to_string("accounts/partials/address_form.html", {
                "address": None,
                "errors": e.messages,
            }, request=request)
            return HttpResponse(html, status=400)

        addresses_html = render_to_string("accounts/partials/address.html", {
            "addresses": Address.objects.filter(user=request.user).order_by("-id")
        }, request=request)

        response_html = (
            f'<div id="shipping-list" hx-swap-oob="true">{addresses_html}</div>'
            f'<div id="shipping-form" hx-swap-oob="true"></div>'
        )
        return HttpResponse(response_html)

    return HttpResponseNotAllowed(["GET", "POST"])


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == "GET":
        return render(request, "accounts/partials/address_form.html", {"address": address})
    if request.method == "POST":
        recipient = request.POST.get("recipient_name", address.recipient_name).strip()
        addr = request.POST.get("address", address.address).strip()
        phone = request.POST.get("phone", address.phone).strip()
        is_default = bool(request.POST.get("is_default"))

        # duplicate check excluding current address
        dup_qs = Address.objects.filter(
            user=request.user,
            recipient_name__iexact=recipient,
            address__iexact=addr,
            phone__iexact=phone
        ).exclude(id=address.id)
        if dup_qs.exists():
            address.recipient_name = recipient
            address.address = addr
            address.phone = phone
            html = render_to_string("accounts/partials/address_form.html", {
                "address": address,
                "errors": ["Địa chỉ trùng với một địa chỉ đã có."],
            }, request=request)
            return HttpResponse(html, status=400)

        address.recipient_name = recipient
        address.address = addr
        address.phone = phone
        address.is_default = is_default
        try:
            address.full_clean()
            address.save()
        except ValidationError as e:
            html = render_to_string("accounts/partials/address_form.html", {
                "address": address,
                "errors": e.messages,
            }, request=request)
            return HttpResponse(html, status=400)

        addresses_html = render_to_string("accounts/partials/address.html", {
            "addresses": Address.objects.filter(user=request.user).order_by("-id")
        }, request=request)
        response_html = (
            f'<div id="shipping-list" hx-swap-oob="true">{addresses_html}</div>'
            f'<div id="shipping-form" hx-swap-oob="true"></div>'
        )
        return HttpResponse(response_html)
    return HttpResponseNotAllowed(["GET", "POST"])


@login_required
def delete_address(request, address_id):
    if request.method not in ("DELETE", "POST"):
        return HttpResponseNotAllowed(["DELETE", "POST"])
    address = get_object_or_404(Address, id=address_id, user=request.user)
    was_default = address.is_default
    address.delete()
    # if we deleted the default, set the newest one as default
    if was_default:
        next_addr = Address.objects.filter(user=request.user).order_by('-id').first()
        if next_addr:
            next_addr.is_default = True
            next_addr.save()
    addresses_html = render_to_string("accounts/partials/address.html", {
        "addresses": Address.objects.filter(user=request.user).order_by("-id")
    }, request=request)
    response_html = (
        f'<div id="shipping-list" hx-swap-oob="true">{addresses_html}</div>'
        f'<div id="shipping-form" hx-swap-oob="true"></div>'
    )
    return HttpResponse(response_html)


@login_required
def set_default_address(request, address_id):
    """Mark given address as default via HTMX (POST)."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    addr = get_object_or_404(Address, id=address_id, user=request.user)
    addr.is_default = True
    addr.save()
    addresses_html = render_to_string("accounts/partials/address.html", {
        "addresses": Address.objects.filter(user=request.user).order_by("-id")
    }, request=request)
    response_html = (
        f'<div id="shipping-list" hx-swap-oob="true">{addresses_html}</div>'
    )
    return HttpResponse(response_html)
