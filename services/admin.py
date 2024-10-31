from django.contrib import admin
from django import forms
from .models import Service, Order, Category, UserBalance
from django.contrib import messages

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
    list_display = ('name',)# Foydalanuvchidan qo'shimcha summa olish uchun forma

    
class AddFundsForm(forms.Form):
    amount = forms.DecimalField(label='Qo\'shmoqchi bo\'lgan summa', min_value=0.01)

@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    actions = ['add_funds']

    def add_funds(self, request, queryset):
        if not request.user.is_superuser:  # Faqat adminlar uchun ruxsat
            self.message_user(request, 'Sizda bu amalni bajarish huquqi yo\'q.', level=messages.ERROR)
            return
        
        if 'apply' in request.POST:
            form = AddFundsForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                for user_balance in queryset:
                    user_balance.balance += amount
                    user_balance.save()
                self.message_user(request, f'Balansga {amount} qo\'shildi.')
                return None
        else:
            form = AddFundsForm()

        return self.render_change_form(
            request, 
            context={'form': form, 'queryset': queryset}, 
            using=self.get_template_names()
        )

    add_funds.short_description = 'Foydalanuvchi balansiga qo\'shish'
