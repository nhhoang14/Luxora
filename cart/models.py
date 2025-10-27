from django.db import models
from django.contrib.auth.models import User
from products.models import Product, Color


# Giỏ hàng
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Cart #{self.id} - {self.user or 'Guest'}"


# Sản phẩm trong giỏ hàng
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        # ✅ Ràng buộc để không trùng sản phẩm cùng màu trong 1 giỏ
        unique_together = ('cart', 'product', 'color')

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        if self.color:
            return f"{self.product.name} ({self.color.name}) x {self.quantity}"
        return f"{self.product.name} x {self.quantity}"
