from django.contrib import admin
from .models import Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "recipient_name", "city", "country", "is_default")
    list_filter = ("country", "is_default")
    search_fields = ("recipient_name", "phone", "city", "line1", "line2")
