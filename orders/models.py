from django.db import models
from django.conf import settings
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Đang xử lý'),
        ('shipping', 'Đang giao'),
        ('completed', 'Thành công'),
        ('cancelled', 'Đã hủy'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    transaction_code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Các đơn hàng"

    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.full_name}"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())

    def can_cancel(self):
        return self.status in ('pending', 'shipping')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Sản phẩm trong đơn hàng"
        verbose_name_plural = "Các sản phẩm trong đơn hàng"

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        if self.product:
            return f"{self.product.name} x {self.quantity}"
        return f"Sản phẩm (đã xóa) x {self.quantity}"
