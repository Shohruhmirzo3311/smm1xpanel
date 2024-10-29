from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import service_list, service_detail_ajax, create_order, order_history, balance_view, top_up_balance, ServiceViewSet, OrderViewSet
from graphene_django.views import GraphQLView
app_name = 'services'

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'orders', OrderViewSet)


urlpatterns = [
    path('services/', service_list, name='service_list'),
    path('balance/view/', balance_view, name='balance_view'),
    path('balance/top-up/', top_up_balance, name='top_up_balance'),
    path('services/<int:service_id>/detail/', service_detail_ajax, name='service_detail_ajax'),
    path('services/<int:service_id>/order/', create_order, name='create_order'),
    path('order/history/', order_history, name='history'),
    path('api/', include(router.urls)),
    path("graphql/", GraphQLView.as_view(graphiql=True)),
]
