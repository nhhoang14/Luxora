from django.shortcuts import render
from django.http import HttpResponse

def order_list(request):
    return HttpResponse("Order list page")
