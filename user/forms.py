from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()
# Foydalanuvchini ro'yxatdan o'tkazish formasi
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        User = get_user_model()
        user = authenticate(username=username, password=password)

        if user is None:
            raise forms.ValidationError("Noto'g'ri login yoki parol.")

        return cleaned_data
