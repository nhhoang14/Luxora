from django.contrib import admin
from .models import Category, Product
from adminsortable2.admin import SortableAdminMixin

@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin): 
    list_display = ('name', 'slug', 'order') 
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'order')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'created_at')
    list_filter = ('categories',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('categories',)