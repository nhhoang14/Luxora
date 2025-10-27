from django.contrib import admin
from django.utils.html import format_html
from adminsortable2.admin import SortableAdminMixin
from .models import Category, Product, Color, ProductImage


# ----------------------------
# Danh mục (Category)
# ----------------------------
@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'order')


# ----------------------------
# Màu sắc (Color)
# ----------------------------
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code', 'color_preview']

    def color_preview(self, obj):
        return format_html(
            '<div style="width:20px;height:20px;background:{};border:1px solid #ccc;border-radius:25px"></div>',
            obj.hex_code
        )
    color_preview.short_description = "Preview"


# ----------------------------
# Ảnh phụ của sản phẩm
# ----------------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'thumbnail')

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:60px;height:60px;object-fit:cover;border-radius:6px;" />', obj.image.url)
        return "-"
    thumbnail.short_description = "Xem trước"


# ----------------------------
# Sản phẩm (Product)
# ----------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'created_at')
    list_filter = ('categories', 'colors')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('categories', 'colors')
    inlines = [ProductImageInline]
