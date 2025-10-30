from django.contrib import admin
from .models import User, Address
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Thông tin thêm", {"fields": ("avatar",)}),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("recipient_name", "phone", "address", "user", "is_default")
    list_filter = ("is_default", "user")
