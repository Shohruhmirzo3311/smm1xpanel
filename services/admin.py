from django.contrib import admin
from django import forms
from .models import Service, Order, Category, UserBalance, Platform , Balance
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


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)# Foydalanuvchidan qo'shimcha summa olish uchun forma


# class AddFundsForm(forms.Form):
#     amount = forms.DecimalField(label="Qo'shmoqchi bo'lgan summa", min_value=0.01)

# @admin.register(UserBalance)
# class UserBalanceAdmin(admin.ModelAdmin):
#     list_display = ("user", "balance")
#     actions = ["add_funds"]

#     def add_funds(self, request, queryset):
#         if not request.user.is_superuser:  # Check if the user is an admin
#             self.message_user(request, "Sizda bu amalni bajarish huquqi yo'q.", level=messages.ERROR)
#             return
        
#         if 'apply' in request.POST:
#             form = AddFundsForm(request.POST)
#             if form.is_valid():
#                 amount = form.cleaned_data['amount']
                
#                 # Check if a UserBalance instance already exists for each user
#                 for user_balance in queryset:
#                     try:
#                         # Ensure that a balance already exists for the user before updating
#                         user_balance.balance += amount
#                         user_balance.save()
#                     except UserBalance.DoesNotExist:
#                         # If no UserBalance exists, raise a validation error
#                         self.message_user(request, f"Foydalanuvchi uchun balans mavjud emas: {user_balance.user}", level=messages.ERROR)
#                         return

#                 self.message_user(request, f"Balansga {amount} qo'shildi.")
#                 return None
#         else:
#             form = AddFundsForm()  # Display an empty form on GET request

#         # Render the form in the admin change interface
#         return self.render_change_form(
#             request, 
#             context={'form': form, 'queryset': queryset}, 
#             using=self.get_template_names()
#         )

#     add_funds.short_description = "Foydalanuvchi balansiga qo'shish"

class AddFundsForm(forms.Form):
    amount = forms.DecimalField(label="Qo'shmoqchi bo'lgan summa", min_value=0.01)

@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ("user", "balance")
    actions = ["add_funds"]

    


admin.site.register(Balance)
# def add_funds(self, request, queryset):
#     if not request.user.is_superuser:  # Ensure only admin can perform this action
#         self.message_user(request, "Sizda bu amalni bajarish huquqi yo'q.", level=messages.ERROR)
#         return

#     if 'apply' in request.POST:
#         form = AddFundsForm(request.POST)
#         if form.is_valid():
#             amount = form.cleaned_data['amount']
#             for user_balance in queryset:
#                 if user_balance:
#                     # Log the balance before and after the update for debugging
#                     self.message_user(request, f"Before update: {user_balance.amount}", level=messages.INFO)
#                     user_balance.update_balance(amount)  # Update balance
#                     user_balance.save()  # Save the updated balance
#                     self.message_user(request, f"Balansga {amount} qo'shildi.", level=messages.SUCCESS)
#                     self.message_user(request, f"After update: {user_balance.amount}", level=messages.INFO)
#                 else:
#                     self.message_user(request, f"Balans topilmadi: {user_balance.user.username}", level=messages.ERROR)
#         else:
#             self.message_user(request, "Formada xatolik mavjud.", level=messages.ERROR)
#     else:
#         form = AddFundsForm()

#     return self.render_change_form(
#         request, 
#         context={'form': form, 'queryset': queryset},
#         using=self.get_template_names()
#     )

