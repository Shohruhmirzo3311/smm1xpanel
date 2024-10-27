from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, UserLoginForm

User = get_user_model()

class UserRegistrationTests(TestCase):

    def setUp(self):
        self.url = reverse('user:register')

    def test_registration_page_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_registration_form_valid(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'StrongPassword1!',
            'password2': 'StrongPassword1!',
        })
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')
        self.assertRedirects(response, reverse('user:login'))

    def test_registration_form_invalid_passwords(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'StrongPassword1!',
            'password2': 'DifferentPassword!',
        })
        self.assertEqual(User.objects.count(), 0)
        self.assertFormError(response, 'form', 'password2', "Parollar mos kelmayapti!")

    def test_registration_form_short_password(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'short',
            'password2': 'short',
        })
        self.assertEqual(User.objects.count(), 0)
        self.assertFormError(response, 'form', 'password1', "Parol kamida 8 ta belgidan iborat bo'lishi kerak.")

class UserLoginTests(TestCase):

    def setUp(self):
        self.url = reverse('user:login')
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='StrongPassword1!')

    def test_login_page_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_login_form_valid(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'StrongPassword1!',
        })
        self.assertEqual(response.status_code, 302)  # Redirects after successful login
        self.assertContains(response, "Xush kelibsiz", status_code=200)  # Assuming you have a welcome message

    def test_login_form_invalid(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'WrongPassword',
        })
        self.assertFormError(response, 'form', None, "Noto'g'ri login yoki parol.")
