from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

def user_avatar_path(instance, filename):
    return f"avatars/{instance.username}/{filename}"

class User(AbstractUser):
    # có sẵn: username, email, password, first_name, last_name
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True, null=True)

    def __str__(self):
        return self.get_full_name() or self.username


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    recipient_name = models.CharField("Tên người nhận", max_length=100)
    phone = models.CharField("Số điện thoại", max_length=20)
    address = models.CharField("Địa chỉ", max_length=255)
    is_default = models.BooleanField("Đặt làm mặc định", default=False)

    class Meta:
        ordering = ["-is_default", "-id"]

    def __str__(self):
        return f"{self.recipient_name} · {self.address}"

    def clean(self):
        """Giới hạn tối đa 3 địa chỉ / user."""
        if not self.pk and self.user.addresses.count() >= 3:
            raise ValidationError("Bạn chỉ có thể lưu tối đa 3 địa chỉ giao hàng.")

    def save(self, *args, **kwargs):
        self.full_clean()  # kiểm tra giới hạn trước khi lưu
        super().save(*args, **kwargs)
        # Nếu đánh dấu mặc định thì bỏ mặc định ở các địa chỉ khác
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)