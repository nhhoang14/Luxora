from django import forms
from django.contrib.auth.models import User
from .models import Profile, Address

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            raise forms.ValidationError('Passwords do not match')
        return cleaned

class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ("full_name","phone","line1","line2","city","state","postal_code","country","is_default")
        widgets = {
            "is_default": forms.CheckboxInput(attrs={"class": "ml-2"}),
        }
