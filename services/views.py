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
from .forms import SearchForm
from .forms import URLSearchForm
from django.contrib.auth import get_user_model
from services.models import Balance

import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .forms import BalanceForm
from .models import Balance
from django.conf import settings




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


logger = logging.getLogger(__name__)
import requests
import logging
from django.shortcuts import render

# Create a logger
logger = logging.getLogger(__name__)

def service_list(request):
    api_url = "https://1xpanel.com/api/v2"
    api_key = "6b1bea025185a663cb0a3b08b6526a60"
    params = {'key': api_key, 'action': 'services'}

    # Define specific categories to match the dropdown options
    predefined_categories = {
        'Instagram': 'Instagram',
        'Telegram': 'Telegram',
        'Twitter': 'Twitter',
        'Facebook': 'Facebook',
        'TikTok': 'TikTok',
        'Other Special': 'Other special'
    }

    try:
        # Fetch service data from API
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            services_data = response.json()
            category_details = {key: [] for key in predefined_categories.values()}
            service_details = {key: [] for key in predefined_categories.values()}

            # Categorize services into predefined categories
            for service in services_data:
                category_name = service.get('category')
                matched_category = next((cat for cat, name in predefined_categories.items() if cat in category_name), None)

                if matched_category:
                    category_details[matched_category].append({
                        'category': service["category"],
                        'service': service['service'],
                        'name': service['name'],
                        'rate': service['rate'],
                        'min': service['min'],
                        'max': service['max'],
                    })
                    
                    service_details[matched_category].append({
                        'service': {
                            'category': service["category"],
                            "service_name": service['service'],
                            'name': service['name'],
                            'min': service['min'],
                            'max': service['max'],
                            'rate': service['rate'],
                        }
                    })

            
                

            if request.method == 'POST':
                print(request.POST)
                if request.user.is_authenticated:
                    user_balans = get_object_or_404(Balance, user=request.user)
                    category = request.POST.get('category')
                    url = request.POST.get('url')
                    number = request.POST.get('number')
                    comment = request.POST.get('comment')
                    answer = request.POST.get('answer')
                    ser_id , total = request.POST.get('total').split('-')
            
                    payload = {
                        'key': api_key,
                        'action': 'add',
                        'service': ser_id,
                        'link': url,
                        'quantity': number,
                    }

                    if comment:
                        payload['comments'] = comment
                    elif answer:
                        payload['answer_number'] = answer
                    print(type(total))

                    # Access the balance field (e.g., `amount`)
                    user_balance = float(user_balans.amount)  # Get the current balance as a float

                    # Check if the balance is enough
                    if user_balance >= float(total):
                        # Update the balance
                        user_balans.amount = user_balans.amount - float(total)  # Deduct the total from the balance
                        user_balans.save()  # Save the updated balance

                        try:
                            post_response = requests.post(api_url, data=payload)
                            response_data = post_response.json()
                            print(f"API Response: {response_data}")
                        except Exception as e:
                            logger.error(f"Error making API request: {e}")
                            response_data = {"error": str(e)}

                        return render(request, 'services/test2.html', {
                            "service_details": service_details,
                            "category_details": category_details,
                            "api_response": response_data,
                        })
                    else:
                        messages.error(request, "Sizning hisobingiz yetarli emas")
                else:
                    return redirect('user:login')

            return render(request, 'services/test2.html', {
                "service_details": service_details,
                "category_details": category_details
            })

        else:
            return render(request, 'services/test2.html', {})

    except requests.exceptions.RequestException as e:
        return render(request, 'services/test2.html', {})




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


class CustomPagination(PageNumberPagination):
    page_size = 10  # Set your desired page size
    page_size_query_param = 'page_size'  # Allows the client to set the page size
    max_page_size = 100  # Limit the maximum page size

def search_view(request):
    form = SearchForm(request.GET or None)
    results = []
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            # Qidiruv logikasi (modelingizdagi kerakli maydon bo‘yicha qidirish)
            results = Service.objects.filter(name__icontains=query)
    
    return render(request, 'services/service_list.html', {'form': form, 'results': results})

@api_view(['GET'])
def service_list_api(request):
    services = Service.objects.select_related('category').all()
    print(f"Services found: {services.count()}")
    paginator = CustomPagination()
    paginated_services = paginator.paginate_queryset(services, request)
    
    serializer = ServiceSerializer(paginated_services, many=True)
    logger.info(f"Paginated services: {serializer.data}") 
    return paginator.get_paginated_response(serializer.data)




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
    try:
        balance = Balance.objects.get(user=request.user)
        logger.info(f"Balance viewed for user: {request.user.id}")
        print(balance)
        # Check if the balance is 0 and set the message accordingly
        if balance.amount == Decimal('0.00'):
            balance_message = "Sizning balansingiz 0 sum"
        else:
            balance_message = f"Sizning balansingiz {balance.amount} sum"

        return render(request, 'services/balance/view.html', {
            'balance': balance,
            'balance_message': balance_message
        })

    except Balance.DoesNotExist:
        logger.warning(f"Balance not found for user: {request.user.id}")
        return render(request, 'services/balance/view.html', {'error': 'Balans topilmadi.'})


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

User = get_user_model()

def create_missing_balances():
    users_without_balance = User.objects.filter(balance__isnull=True)
    for user in users_without_balance:
        Balance.objects.create(user=user)
    print("Missing balances created.")


@login_required
def top_up_balance(request):
    cards = [
        {"number": "6262 5700 8436 5560", "holder": "Mahmudov Muhammadjon"},
        {"number": "4073 4200 5464 1489", "holder": "Mahmudov Muhammadjon"}
    ]
    return render(request, 'services/balance/top_up.html', {'cards': cards})


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




def url_search_view(request):
    form = URLSearchForm(request.POST or None)  # Use POST or None to handle GET requests as well
    if request.method == 'POST' and form.is_valid():
        # Get the URL from the cleaned data
        url = form.cleaned_data['url']
        # URL can be further processed here if needed
        
        # Render the result page with the cleaned URL
        return render(request, 'services/test.html', {'form': form, 'url': url})

    # In case of GET or invalid form submission, just render the form
    return render(request, 'services/test.html', {'form': form})








def send_to_telegram(user, balance, picture_url):
    bot_token = "7590906432:AAG5_Gt6LBl6TnS2lY60fx8Rlfl7FxSWq3A"
    chat_id = -1004523571009
    
    
    message = f"User: {user.username}\nBalance Added: {balance} UZS\nProfile Picture: {picture_url}"
    
    # Send the text message to the Telegram group
    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    
    # Send the request to Telegram
    try:
        response = requests.post(telegram_url, data=payload)
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Error sending message: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
