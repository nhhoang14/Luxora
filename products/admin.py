from django.contrib import admin
from .models import Category, Product, ProductImage
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin): 
    list_display = ('name', 'slug', 'order') 
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'order')

class ProductImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'order')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'created_at')
    list_filter = ('categories',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('categories',)
    inlines = [ProductImageInline]