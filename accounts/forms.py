from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng.")
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Tên đăng nhập", max_length=100)
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput)

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        field_attrs = {
            'class': 'mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 pr-12 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm',
        }

        self.fields['old_password'].widget.attrs.update({
            **field_attrs,
            'id': 'id_old_password',
            'placeholder': 'Mật khẩu hiện tại',
        })
        self.fields['new_password1'].widget.attrs.update({
            **field_attrs,
            'id': 'id_new_password1',
            'placeholder': 'Mật khẩu mới',
        })
        self.fields['new_password2'].widget.attrs.update({
            **field_attrs,
            'id': 'id_new_password2',
            'placeholder': 'Nhập lại mật khẩu mới',
        })
