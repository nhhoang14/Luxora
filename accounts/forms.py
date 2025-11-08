
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Address, Profile

User = get_user_model()

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'line1', 'line2', 'city', 'state', 'postal_code', 'country', 'is_default']

class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
