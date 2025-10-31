from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'subtotal_display')

    def subtotal_display(self, obj):
        # trả giá trị subtotal nếu model có thuộc tính/field subtotal,
        # nếu không tính tạm bằng quantity * price (nếu có)
        try:
            if hasattr(obj, 'subtotal'):
                return obj.subtotal
            qty = getattr(obj, 'quantity', None) or 0
            price = getattr(obj, 'price', None) or 0
            return qty * price
        except Exception:
            return ''
    subtotal_display.short_description = 'Thành tiền'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'total_amount_display')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'id')
    inlines = [OrderItemInline]

    def total_amount_display(self, obj):
        # trả total_amount nếu model có, nếu không cộng tay từ items
        try:
            if hasattr(obj, 'total_amount'):
                return obj.total_amount
            total = 0
            for it in getattr(obj, 'items', []).all():
                qty = getattr(it, 'quantity', 0) or 0
                price = getattr(it, 'price', 0) or 0
                total += qty * price
            return total
        except Exception:
            return ''
    total_amount_display.short_description = 'Tổng tiền'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    search_fields = ('product__name',)
