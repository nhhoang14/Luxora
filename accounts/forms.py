from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "recipient_name", "phone", "line1", "line2",
            "city", "state", "country", "postal_code", "is_default"
        ]
