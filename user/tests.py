from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .forms import UserRegistrationForm, UserLoginForm
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta

User = get_user_model()

class UserRegistrationFormTests(TestCase):
    def test_valid_registration_form(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), "Form should be valid for correct data")
        
        
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('Password123!'))
    
    def test_password_mismatch(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Password123!',
            'password2': 'Password1234!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Parollar mos kelmayapti!", form.errors['password2'])

    def test_user_creation(self):
        # Test foydalanuvchini yaratish
        user = User.objects.create_user(username='testuser', email='test@example.com', password='Password123!')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('Password123!'))

    
    def test_weak_password(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'weakpass',
            'password2': 'weakpass',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Parolda kamida bitta raqam bo'lishi kerak.", form.errors['password2'])

    def test_missing_digit_in_password(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Password!',
            'password2': 'Password!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Parolda kamida bitta raqam bo'lishi kerak.", form.errors['password2'])


class UserLoginFormTests(TestCase):
    def test_invalid_login(self):
        form_data = {
            'username': 'nonexistentuser',
            'password': 'wrongpassword',
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Noto'g'ri login yoki parol.", form.errors['__all__'])


class UserRegistrationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('user:register')

    def test_successful_registration(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ro\'yxatdan o\'tish muvaffaqiyatli')

    def test_existing_username_error(self):
        User.objects.create_user(username='existinguser', password='password123')
        data = {
            'username': 'existinguser',
            'email': 'user@example.com',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }
        response = self.client.post(self.register_url, data)
        self.assertContains(response, 'Bu foydalanuvchi nomi allaqachon mavjud')

class EmailVerificationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com')
        self.verify_url = reverse('user:verify_email')

    def test_correct_verification_code(self):
        self.client.session['verification_code'] = '123456'
        self.client.session['user_email'] = self.user.email
        self.client.session['verification_time'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        response = self.client.post(self.verify_url, {'verification_code': '123456'})
        self.user.refresh_from_db()
        self.assertFalse(self.user.email_verified)
        self.assertRedirects(response, reverse('user:login'))

    def test_expired_verification_code(self):
        self.client.session['verification_code'] = '123456'
        self.client.session['user_email'] = self.user.email
        self.client.session['verification_time'] = (timezone.now() - timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
        response = self.client.post(self.verify_url, {'verification_code': '123456'})
        messages = list(response.context['messages'])
        if messages:
            self.assertEqual(str(messages[0]), 'Tasdiqlash kodi muddati o\'tgan.')

    def test_incorrect_verification_code(self):
        self.client.session['verification_code'] = '123456'
        self.client.session['user_email'] = self.user.email
        response = self.client.post(self.verify_url, {'verification_code': '654321'})






# import requests


# import random


# password = random.randint(1000, 9999)

# print(password)

# print(password == int(input('password')))