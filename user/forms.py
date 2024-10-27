from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 != password2:
            raise ValidationError("Parollar mos kelmayapti!")

        # Password strength checks
        if len(password1) < 8:
            raise ValidationError("Parol kamida 8 ta belgidan iborat bo'lishi kerak.")
        if not any(char.isdigit() for char in password1):
            raise ValidationError("Parolda kamida bitta raqam bo'lishi kerak.")
        if not any(char.isupper() for char in password1):
            raise ValidationError("Parolda kamida bitta katta harf bo'lishi kerak.")
        if not any(char.islower() for char in password1):
            raise ValidationError("Parolda kamida bitta kichik harf bo'lishi kerak.")
        if not any(char in "!@#$%^&*()" for char in password1):
            raise ValidationError("Parolda kamida bitta maxsus belgi (misol: @, #, $, ...) bo'lishi kerak.")

        return password2


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            raise forms.ValidationError("Noto'g'ri login yoki parol.")

        return cleaned_data
