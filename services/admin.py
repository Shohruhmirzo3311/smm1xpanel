from django.contrib import admin
from .models import Service, Order, Category

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform', 'category', 'base_price', 'price', 'completion_time')
    search_fields = ('name', 'platform')
    list_filter = ('platform', 'category')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'created_at', 'is_completed')
    list_filter = ('is_completed', 'created_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)