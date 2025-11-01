from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.db import transaction
from django.db.models import F
from .forms import RegisterForm, AvatarForm, AddressForm
from .models import Address, Order

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    avatar_form = AvatarForm(instance=request.user.profile)
    return render(request, 'accounts/profile.html', {'avatar_form': avatar_form})

@login_required
def update_avatar(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')
    form = AvatarForm(request.POST, request.FILES, instance=request.user.profile)
    if form.is_valid():
        form.save()
        return render(request, 'accounts/_avatar_partial.html')
    return HttpResponseBadRequest('Invalid form')

# ---------- Addresses ----------
@login_required
def address_list(request):
    form = AddressForm()
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/addresses/list.html', {'form': form, 'addresses': addresses})

@login_required
def address_create(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')
    form = AddressForm(request.POST)
    if form.is_valid():
        addr = form.save(commit=False)
        addr.user = request.user
        if addr.is_default:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        addr.save()
        addresses = Address.objects.filter(user=request.user)
        return render(request, 'accounts/addresses/_list_partial.html', {'addresses': addresses})
    return HttpResponseBadRequest('Invalid form')

@login_required
def address_edit(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=addr)
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.is_default:
                Address.objects.filter(user=request.user, is_default=True).exclude(pk=addr.pk).update(is_default=False)
            obj.save()
            addresses = Address.objects.filter(user=request.user)
            return render(request, 'accounts/addresses/_list_partial.html', {'addresses': addresses})
        return HttpResponseBadRequest('Invalid form')
    else:
        form = AddressForm(instance=addr)
        return render(request, 'accounts/addresses/_form_partial.html', {'form': form, 'addr': addr})

@login_required
def address_delete(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')
    addr.delete()
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/addresses/_list_partial.html', {'addresses': addresses})

@login_required
def address_set_default(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')
    with transaction.atomic():
        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        addr.is_default = True
        addr.save()
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/addresses/_list_partial.html', {'addresses': addresses})

# ---------- Orders ----------
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'accounts/orders/list.html', {'orders': orders})
