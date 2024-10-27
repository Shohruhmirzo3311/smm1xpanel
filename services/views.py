from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import Service, Order, Category, Balance
from .serializers import ServiceSerializer, OrderSerializer
from django.utils import timezone
from django.contrib.auth.models import User

# HTML-based views
def service_list(request):
    services = Service.objects.all()
    categories = Category.objects.prefetch_related('service_set').all()
    return render(request, 'services/service_list.html', {'services': services})

@login_required
def service_detail_ajax(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'services/service_detail_ajax.html', {'service': service})


@login_required
def create_order(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    order = Order.objects.create(user=request.user, service=service)
    return redirect('orders/history')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/history.html', {'orders': orders})


def balance_view(request):
    if request.user.is_authenticated:
        try:
            balance = Balance.objects.get(user=request.user)  # Foydalanuvchi balansini olish
            return render(request, 'services/balance/view.html', {'balance': balance})
        except Balance.DoesNotExist:
            return render(request, 'services/balance/view.html', {'error': 'Balans topilmadi.'})
    else:
        return redirect('user:login')  # Foydalanuvchi tizimga kirgan bo'lishi kerak


@login_required  # Foydalanuvchini autentifikatsiya qilish
def top_up_balance(request):
    site_card_number = "1234 5678 9012 3456"  # Saytning karta raqami

    return render(request, 'services/balance/top_up.html', {'site_card_number': site_card_number})


# DRF API views
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


