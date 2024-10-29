from django.test import TestCase
from .models import UserBalance, Service, Order, Category
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.admin.sites import site
from .admin import ServiceAdmin
from .models import Service
from decimal import Decimal
from unittest.mock import patch


User = get_user_model()

class UserBalanceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user_balance = UserBalance.objects.create(user=self.user, balance=100.00)

    def test_balance_update(self):
        self.user_balance.update_balance(50.00)
        self.assertEqual(self.user_balance.balance, 150.00)

    def test_sufficient_balance(self):
        self.assertTrue(self.user_balance.has_sufficient_balance(50.00))
        self.assertFalse(self.user_balance.has_sufficient_balance(150.00))

class ServiceTest(TestCase):
    def setUp(self):
        # Sinov uchun xizmat obyektini yaratamiz
        self.service = Service.objects.create(
            name="Test Service",
            platform="Instagram",
            category=self.category,
            base_price=Decimal('10.0'),  # Decimal formatida bazaviy narx
        )

    def test_save_method(self):
        # Narx 30% foyda bilan o'zgartirilganligini tekshirish
        self.service.save()
        expected_price = self.service.base_price * Decimal('1.3')
        self.assertEqual(self.service.price, expected_price)

    @patch('services.models.requests.get')
    def test_update_price(self, mock_get):
        # Soxta API javobi
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {'base_price': '15.00'}

        # update_price metodini chaqirish
        self.service.update_price()

        # Kutilayotgan qiymatlarni tekshirish
        new_base_price = Decimal('15.00')
        expected_price = new_base_price * Decimal('1.3')
        
        self.assertEqual(self.service.base_price, new_base_price)
        self.assertEqual(self.service.price, expected_price)

class AdminTest(TestCase):
    def setUp(self):
        self.service_admin = ServiceAdmin(Service, site)

    def test_list_display(self):
        self.assertIn('name', self.service_admin.list_display)
        self.assertIn('platform', self.service_admin.list_display)



class OrderViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_order_creation(self):
        response = self.client.post(reverse('services:create_order', args=[self.service.id]), {
            'service_id': 1,  # Bu yerda mos ravishda servis ID sini berish kerak
        })
        self.assertEqual(response.status_code, 302)  # Redirect bo'lishi kerak
        self.assertTrue(Order.objects.filter(user=self.user).exists())
