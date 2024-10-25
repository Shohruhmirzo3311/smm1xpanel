from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# Foydalanuvchini ro'yxatdan o'tkazish formasi
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Foydalanuvchini tizimga kirish formasi
class UserLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False)  # Esda saqlash opsiyasi qo'shildi

    class Meta:
        model = User
        fields = ['username', 'password']
