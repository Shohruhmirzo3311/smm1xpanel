from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Service, Order, Category, Balance, Platform
from .serializers import ServiceSerializer,CategorySerializer, OrderSerializer
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.cache import cache
import logging
logger = logging.getLogger(__name__)
from rest_framework.decorators import action
from rest_framework.response import Response
import requests
from django.http import JsonResponse

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
    url = f"http://your_api_url/guarantee/{service_id}/"  # O'zgartirish talab qilinadi

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


# HTML-based views
def service_list(request):
    categories = Category.objects.prefetch_related('service_set').all()


    youtube_services = Service.objects.filter(category__name="YouTube")
    telegram_services = Service.objects.filter(category__name="Telegram")
    instagram_services = Service.objects.filter(category__name="Instagram")
    
    context = {
        'categories': categories,
        'youtube_services': youtube_services,
        'telegram_services': telegram_services,
        'instagram_services': instagram_services,
    }
    return render(request, 'services/service_list.html', context)


logger = logging.getLogger(__name__)

class category_list_api(APIView):
    def get(self, request, platform_name):
        logger.info(f"Platform name received: {platform_name}")
        try:
            platform = Platform.objects.get(name=platform_name)
            categories = Category.objects.filter(service__platform=platform)
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Platform.DoesNotExist:
            return Response({'error': 'Platform not found'}, status=status.HTTP_404_NOT_FOUND)

def service_list_api(request):
    services = Service.objects.select_related('category').all().values(
        'id', 'name', 'description', 'completion_time', 'order_speed', 'category__name'
    )
    return JsonResponse(list(services), safe=False)


class CategoryList(APIView):
    def get(self, request, platform=None):
        if platform and platform != 'all':
            categories = Category.objects.filter(platform=platform)  # platformga mos keluvchi kategoriyalar
        else:
            categories = Category.objects.all()  # Barcha kategoriyalar

        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
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


@login_required
def create_order(request, service_id):
    try:
        service = get_object_or_404(Service, id=service_id)
        order = Order.objects.create(user=request.user, service=service)
        logger.info(f"Order created: {order.id} for user: {request.user.id}")
        return redirect('orders/history')
    except Exception as e:
        logger.error(f"Error creating order for service {service_id}: {e}")
        return redirect('services/service_list')


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


@login_required  # Foydalanuvchini autentifikatsiya qilish
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

