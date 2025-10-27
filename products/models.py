import os
from django.conf import settings
from django.db import models
from django.utils.text import slugify

# Màu sắc sản phẩm
class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7, help_text="Ví dụ: #FF0000 cho màu đỏ")

    def __str__(self):
        return f"{self.name} ({self.hex_code})"


# Danh mục sản phẩm
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_image(self, ext_list=['jpg', 'png', 'webp']):
        for ext in ext_list:
            path = f'core/images/categories/{self.slug}.{ext}'
            full_path = os.path.join(settings.STATIC_ROOT, path)
            if os.path.exists(full_path):
                return path
        return 'core/images/default-category.jpg'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']


# Sản phẩm
class Product(models.Model):
    categories = models.ManyToManyField('Category', related_name='products', blank=True)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    colors = models.ManyToManyField('Color', related_name='products', blank=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Ảnh phụ (gallery) cho sản phẩm
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Ảnh của {self.product.name}"
