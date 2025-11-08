
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import RegisterForm, AddressForm, AvatarForm
from .models import Address, Profile

# -------------- Auth --------------
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created.')
            return redirect('/accounts/profile/')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/accounts/profile/')
    else:
        form = AuthenticationForm(request)
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')

# -------------- Profile + Avatar --------------
@login_required
def profile_view(request):
    prof, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = AvatarForm(request.POST, request.FILES, instance=prof)
        if form.is_valid():
            form.save()
            messages.success(request, 'Avatar updated')
            return redirect('/accounts/profile/')
    else:
        form = AvatarForm(instance=prof)
    return render(request, 'accounts/profile.html', {'form': form})

# -------------- Addresses (HTMX-friendly) --------------
@login_required
def address_list(request):
    addrs = request.user.addresses.all()
    return render(request, 'accounts/address.html', {'addresses': addrs})

@login_required
def address_create(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            if addr.is_default:
                request.user.addresses.update(is_default=False)
            addr.save()
            if request.headers.get('HX-Request'):
                return render(request, 'accounts/partials/address_item.html', {'a': addr})
            return redirect('/accounts/addresses/')
    else:
        form = AddressForm()
    return render(request, 'accounts/address_form.html', {'form': form})

@login_required
def address_edit(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=addr)
        if form.is_valid():
            addr = form.save()
            if addr.is_default:
                request.user.addresses.exclude(pk=addr.pk).update(is_default=False)
            if request.headers.get('HX-Request'):
                return render(request, 'accounts/partials/address_item.html', {'a': addr})
            return redirect('/accounts/addresses/')
    else:
        form = AddressForm(instance=addr)
    return render(request, 'accounts/address_form.html', {'form': form, 'object': addr})

@login_required
@require_POST
def address_delete(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    addr.delete()
    if request.headers.get('HX-Request'):
        return HttpResponse('')
    return redirect('/accounts/addresses/')

@login_required
@require_POST
def address_set_default(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    request.user.addresses.update(is_default=False)
    addr.is_default = True
    addr.save()
    if request.headers.get('HX-Request'):
        # return refreshed list
        addrs = request.user.addresses.all()
        return render(request, 'accounts/partials/address_list.html', {'addresses': addrs})
    return redirect('/accounts/addresses/')
