import os
from django.conf import settings
from django.db import models
from django.utils.text import slugify

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

# Model cho ảnh sản phẩm
class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.product.name}"

# Sản phẩm
class Product(models.Model):
    categories = models.ManyToManyField('Category', related_name='products', blank=True)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=0)
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

    # Property để lấy tất cả ảnh (bao gồm ảnh chính và ảnh phụ)
    @property
    def all_images(self):
        images = list(self.images.all())
        if self.image and not any(img.image == self.image for img in images):
            # Tạo một ProductImage ảo cho ảnh chính nếu chưa có trong images
            from django.core.files.images import ImageFile
            virtual_image = ProductImage(product=self, image=self.image, order=0)
            images.insert(0, virtual_image)
        return images if images else [None]