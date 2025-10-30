from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cod', 'Thanh toán khi nhận hàng'),
        ('bank', 'Chuyển khoản'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    transaction_code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Đang xử lý')

    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.full_name}"

    @property
    def total_amount(self):
        """Tổng tiền của đơn hàng (sử dụng các OrderItem liên kết)."""
        return sum(item.subtotal for item in self.items.all())

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Các đơn hàng"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        """Tổng tiền của từng dòng sản phẩm."""
        return self.price * self.quantity

    def __str__(self):
        if self.product:
            return f"{self.product.name} x {self.quantity}"
        return f"Sản phẩm (đã xóa) x {self.quantity}"
