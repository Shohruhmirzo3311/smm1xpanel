from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import Service, Order, Category
from .serializers import ServiceSerializer, OrderSerializer
from django.utils import timezone

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


# DRF API views
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


