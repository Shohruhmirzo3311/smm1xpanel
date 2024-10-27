from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import service_list, service_detail_ajax, create_order, order_history, ServiceViewSet, OrderViewSet

app_name = 'services'

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'orders', OrderViewSet)


urlpatterns = [
    path('services/', service_list, name='service_list'),
    path('services/<int:service_id>/detail/', service_detail_ajax, name='service_detail_ajax'),
    path('services/<int:service_id>/order/', create_order, name='create_order'),
    path('order/history/', order_history, name='history'),
    path('api/', include(router.urls)),
]
