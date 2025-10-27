from django.contrib import admin
from .models import Category, Product, Color
from django.utils.html import format_html
from adminsortable2.admin import SortableAdminMixin

@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin): 
    list_display = ('name', 'slug', 'order') 
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'order')

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code', 'color_preview']

    def color_preview(self, obj):
        return format_html(
            '<div style="width:20px;height:20px;background:{};border:1px solid #ccc;border-radius:4px;border-radius:25px"></div>',
            obj.hex_code
        )
    color_preview.short_description = "Preview"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'created_at')
    list_filter = ('categories', 'colors')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('categories', 'colors')
    