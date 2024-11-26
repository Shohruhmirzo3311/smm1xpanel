# /from django.test import TestCase
# from .models import UserBalance, Service, Order, Category
# from django.contrib.auth import get_user_model
# from django.urls import reverse
# from django.contrib.admin.sites import site
# from .admin import ServiceAdmin
# from .models import Service, Platform
# from decimal import Decimal
# from unittest.mock import patch


# User = get_user_model()


# class UserBalanceTest(TestCase):

#     def setUp(self):
#         # Sinov foydalanuvchisini yaratish
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.user_balance = UserBalance.objects.create(user=self.user, balance=Decimal('0.00'))

#     def test_balance_update(self):
#         # Balansni yangilash
#         self.user_balance.update_balance(50.00)
        
#         # Yangilangan balansni tekshirish
#         self.assertEqual(self.user_balance.balance, Decimal('50.00'))

#     def test_balance_update_with_negative_amount(self):
#         # Manfiy balansni yangilash
#         self.user_balance.update_balance(-10.00)
        
#         # Yangilangan balansni tekshirish
#         self.assertEqual(self.user_balance.balance, Decimal('-10.00'))

#     def test_balance_update_with_non_decimal_amount(self):
#         # Qayta ishlash va notog'ri qiymat bilan yangilash
#         self.user_balance.update_balance("20.00")  # string sifatida
#         self.assertEqual(self.user_balance.balance, Decimal('20.00'))

# class ServiceTest(TestCase):
#     def setUp(self):
#         self.category = Category.objects.create(name='Test Category')
#         self.platform = Platform.objects.create(name='Test Platform')  # Platform obyektini yaratish
#         self.service = Service.objects.create(name='Test Service', category=self.category, platform=self.platform)  # Platform ni berish

#     def test_save_method(self):
#         # Narx 30% foyda bilan o'zgartirilganligini tekshirish
#         self.service.save()
#         expected_price = self.service.base_price * Decimal('1.3')
#         self.assertEqual(self.service.price, expected_price)

#     @patch('services.models.requests.get')
#     def test_update_price(self, mock_get):
#         # Soxta API javobi
#         mock_response = mock_get.return_value
#         mock_response.status_code = 200
#         mock_response.json.return_value = {'base_price': '15.00'}

#         # update_price metodini chaqirish
#         self.service.update_price()

#         # Kutilayotgan qiymatlarni tekshirish
#         new_base_price = Decimal('0.00')
#         expected_price = new_base_price * Decimal('1.3')
        
#         self.assertEqual(self.service.base_price, new_base_price)
#         self.assertEqual(self.service.price, expected_price)

# class AdminTest(TestCase):
#     def setUp(self):
#         self.service_admin = ServiceAdmin(Service, site)

#     def test_list_display(self):
#         self.assertIn('name', self.service_admin.list_display)
#         self.assertIn('platform', self.service_admin.list_display)



# class OrderViewTest(TestCase):
#     def setUp(self):
#         self.category = Category.objects.create(name='Test Category')
#         self.platform = Platform.objects.create(name='Test Platform')  # Add this line
#         self.service = Service.objects.create(
#             name='Test Service',
#             category=self.category,
#             platform=self.platform  # Provide the platform
#         )