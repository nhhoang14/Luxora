from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    recipient_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    line1 = models.CharField("Địa chỉ dòng 1", max_length=255)
    line2 = models.CharField("Địa chỉ dòng 2", max_length=255, blank=True)
    city = models.CharField("Thành phố", max_length=100)
    state = models.CharField("Tỉnh/TP", max_length=100, blank=True)
    country = models.CharField("Quốc gia", max_length=100, default="Vietnam")
    postal_code = models.CharField("Mã bưu điện", max_length=20, blank=True)
    is_default = models.BooleanField("Đặt làm mặc định", default=False)

    class Meta:
        ordering = ["-is_default", "-id"]

    def __str__(self):
        return f"{self.recipient_name} · {self.city}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
