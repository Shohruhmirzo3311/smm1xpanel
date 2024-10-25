from rest_framework import serializers
from .models import Service, Order
from django.utils import timezone
from datetime import timedelta

class ServiceSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'platform', 'completion_time', 'price']

    def get_price(self, obj):
        # Narxni foydalanuvchiga 30% foyda bilan ko'rsatadi
        return obj.base_price * 1.3

class OrderSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)  # Narxni va xizmat haqida batafsil ma'lumotni qaytarish uchun
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source='service', write_only=True)  # Buyurtma yaratishda xizmatni ID bo'yicha tanlash
    time_left = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'service', 'service_id', 'created_at', 'expected_completion_time', 'is_completed', 'time_left']

    def get_time_left(self, obj):
        # Qancha vaqt qolgani haqida ma'lumot qaytaradi
        remaining_time = obj.expected_completion_time - timezone.now()
        return remaining_time if remaining_time.total_seconds() > 0 else timedelta(0)

    def create(self, validated_data):
        # Buyurtmani avtomatik ravishda foydalanuvchi va xizmat ma'lumotlari bilan yaratadi
        service = validated_data['service']
        user = self.context['request'].user
        expected_completion_time = timezone.now() + timedelta(minutes=service.completion_time)
        order = Order.objects.create(
            user=user, 
            service=service, 
            expected_completion_time=expected_completion_time
        )
        return order
