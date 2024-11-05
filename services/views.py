from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Service, Order, Category, Balance, UserBalance, Platform
from .serializers import ServiceSerializer,CategorySerializer, OrderSerializer
from django.core.cache import cache
import logging
logger = logging.getLogger(__name__)
from rest_framework.decorators import action
from rest_framework.response import Response
import requests
from django.http import HttpResponse
from rest_framework.decorators import api_view
import decimal
from decimal import Decimal
from django.contrib import messages


# Logger yaratish
logger = logging.getLogger(__name__)

def get_guarantee_from_api(service_id):
    """
    Berilgan service_id orqali API dan kafolat ma'lumotlarini olish.
    
    Args:
        service_id (int): Xizmat identifikatori.
        
    Returns:
        dict: Kafolat ma'lumotlari yoki None.
    """
    # API manzilini o'rnating
    url = f"http://localhost:8000/api/guarantee/{service_id}/"

    try:
        # API ga so'rov yuborish
        response = requests.get(url)

        # So'rov natijasini tekshirish
        if response.status_code == 200:
            guarantee_data = response.json().get('guarantee')
            logger.info(f"Kafolat ma'lumotlari muvaffaqiyatli olindi: {guarantee_data}")
            return guarantee_data  # Kafolat ma'lumotini qaytarish
        else:
            logger.error(f"API ga so'rov xato: {response.status_code} - {response.text}")
            return None  # Agar ma'lumot topilmasa, None qaytarish
    except requests.exceptions.RequestException as e:
        logger.error(f"API ga so'rov yuborishda xato: {e}")
        return None  # Agar xato bo'lsa, None qaytarish


# logger = logging.getLogger(__name__)

# def service_list(request):
#     categories = Category.objects.prefetch_related('service_set').all()
#     all_services = Service.objects.all()
#     context = {
#         'categories': categories,
#         'services': all_services,
#     }
#     return render(request, 'services/service_list.html', context)


def service_list(request):
    categories = Category.objects.prefetch_related('service_set').all()
    all_services = Service.objects.all()
    
    query = request.GET.get('q')
    if query:
        all_services = all_services.filter(name__icontains=query)

    logger.info(f"Total services found: {all_services.count()}")
    
    context = {
        'categories': categories,
        'services': all_services,
    }
    return render(request, 'services/service_list.html', context)


class category_list_api(APIView):
    def get(self, request, platform_name):
        logger.info(f"Platform name received: {platform_name}")
        try:
            platform = Platform.objects.get(name=platform_name)
            categories = Category.objects.filter(service__platform=platform)
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Platform.DoesNotExist:
            logger.error('Platform not found')
            return Response({'error': 'Platform not found'}, status=status.HTTP_404_NOT_FOUND)


# class category_list_api(APIView):
#     def get(self, request, platform_name):
#         logger.info(f"Platform name received: {platform_name}")
#         try:
#             platform = Platform.objects.get(name=platform_name)
#             categories = Category.objects.filter(service__platform=platform)
#             serializer = CategorySerializer(categories, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Platform.DoesNotExist:
#             logger.error('Platform not found')
#             return Response({'error': 'Platform not found'}, status=status.HTTP_404_NOT_FOUND)


class CustomPagination(PageNumberPagination):
    page_size = 10  # Set your desired page size
    page_size_query_param = 'page_size'  # Allows the client to set the page size
    max_page_size = 100  # Limit the maximum page size


@api_view(['GET'])
def service_list_api(request):
    services = Service.objects.select_related('category').all()
    print(f"Services found: {services.count()}")
    paginator = CustomPagination()
    paginated_services = paginator.paginate_queryset(services, request)
    
    serializer = ServiceSerializer(paginated_services, many=True)
    logger.info(f"Paginated services: {serializer.data}") 
    return paginator.get_paginated_response(serializer.data)


# @api_view(['GET'])
# def service_list_api(request):
#     services = Service.objects.select_related('category').all()
#     print(f"Services found: {services.count()}")
#     paginator = CustomPagination()
#     paginated_services = paginator.paginate_queryset(services, request)
    
#     serializer = ServiceSerializer(paginated_services, many=True)
#     return paginator.get_paginated_response(serializer.data)


class CategoryList(APIView):
    def get(self, request, platform=None):
        if platform and platform != 'all':
            categories = Category.objects.filter(platform=platform)  # platformga mos keluvchi kategoriyalar
        else:
            categories = Category.objects.all()  # Barcha kategoriyalar

        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


# class CategoryList(APIView):
#     def get(self, request, platform=None):
#         if platform and platform != 'all':
#             categories = Category.objects.filter(platform=platform)  # platformga mos keluvchi kategoriyalar
#         else:
#             categories = Category.objects.all()  # Barcha kategoriyalar

#         serializer = CategorySerializer(categories, many=True)
#         return Response(serializer.data)
    
@login_required
def service_detail_ajax(request, service_id):
    # Cache key yaratish
    cache_key = f'service_{service_id}'
    service = cache.get(cache_key)
    
    if not service:
        service = get_object_or_404(Service, id=service_id)
        cache.set(cache_key, service, timeout=60*15)  # 15 daqiqaga saqlash
    
    guarantee = get_guarantee_from_api(service_id)
    
    return render(request, 'services/service_detail_ajax.html', {
        'service': service,
        'price': service.price,
        'completion_time': service.completion_time,
        'guarantee': guarantee
    })

# Yangi versiya
@login_required
def create_order(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    total_price = Decimal(service.price)

    try:
        user_balance = UserBalance.objects.get(user=request.user)

        if user_balance.balance < total_price:
            messages.error(request, "Hisobingizda yetarli mablag' mavjud emas.")
            return redirect('services:service_list')  # To'liq nomdan foydalanish

        order = Order.objects.create(
            user=request.user,
            service=service,
            total_price=total_price
        )

        user_balance.balance -= total_price
        user_balance.save()

        messages.success(request, "Buyurtma muvaffaqiyatli yaratildi.")
        logger.info(f"Order created: {order.id} for user: {request.user.id}")
        return redirect('services:history')  # To'liq nomdan foydalanish
        
    except UserBalance.DoesNotExist:
        messages.error(request, "Hisobingiz topilmadi. Iltimos, hisobingizni to'ldiring.")
        return redirect('services:service_list')  # To'liq nomdan foydalanish
        
    except Exception as e:
        logger.error(f"Error creating order for service {service_id}: {e}")
        messages.error(request, "Buyurtma yaratishda xato yuz berdi. Iltimos, qaytadan urinib ko'ring.")
        return redirect('services:service_list')  # To'liq nomdan foydalanish

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).select_related('service').order_by('-created_at')
    return render(request, 'orders/history.html', {'orders': orders})


@login_required
def balance_view(request):
    
    if request.user.is_authenticated:
        try:
            balance = Balance.objects.get(user=request.user)
            logger.info(f"Balance viewed for user: {request.user.id}")
            return render(request, 'services/balance/view.html', {'balance': balance})
        except Balance.DoesNotExist:
            logger.warning(f"Balance not found for user: {request.user.id}")
            return render(request, 'services/balance/view.html', {'error': 'Balans topilmadi.'})
    else:
        return redirect('user:login')


logger = logging.getLogger(__name__)


def update_balance(user, amount):
    try:
        # Balansni olish
        balance = Balance.objects.get(user=user)

        # Balansni yangilash
        balance.balance = Decimal(balance.balance) + Decimal(amount)  # float bo'lsa, to'g'ridan-to'g'ri decimal ga aylantirish
        balance.save()  # O'zgarishlarni saqlash
        logger.info(f"Balance updated for user: {user.id}, new balance: {balance.balance}")

    except Balance.DoesNotExist:
        logger.warning(f"Cannot update balance, not found for user: {user.id}")
        raise ValueError("Balans topilmadi, yangilanish amalga oshirilmadi.")

@login_required
def top_up_balance(request):
    site_card_number = "1234 5678 9012 3456"  # Saytning karta raqami
    return render(request, 'services/balance/top_up.html', {'site_card_number': site_card_number})


# DRF API views
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]  # Foydalanuvchilar uchun ruxsat


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        orders_data = request.data  # JSON orqali ma’lumotlar qabul qilinadi
        orders = [
            Order(user=request.user, service_id=data['service_id'], quantity=data['quantity'])
            for data in orders_data
        ]
        Order.objects.bulk_create(orders)
        return Response({'status': 'Bulk orders created'})

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

def update_service_price(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    service.update_price()  # Modeldagi update_price funksiyasini chaqirish
    return HttpResponse(f"{service.name} narxi yangilandi.")
