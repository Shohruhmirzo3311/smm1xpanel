import random
import smtplib
from datetime import timedelta  # Ensure timedelta is imported
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, 
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from .forms import UserCreationForm
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from .forms import UserRegistrationForm
import re
from django.contrib.auth.forms import PasswordResetForm
from datetime import datetime
from django.http import JsonResponse    
from django.utils import timezone

User = get_user_model()


def send_verification_email(request, user_email, verification_code):
    subject = "Email Tasdiqlash"
    message = f"Sizning tasdiqlash kodingiz: {verification_code}"
    full_email = f"Subject: {subject}\n\n{message}"

    try:
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(settings.EMAIL_HOST_USER, user_email, full_email)
    except Exception as e:
        messages.error(request, "Email yuborishda xatolik yuz berdi.")



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            
            # Username mavjudligini tekshirish
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Bu foydalanuvchi nomi allaqachon mavjud. Iltimos, boshqa nom tanlang.')
                return render(request, 'user/register.html', {'form': form})

            # Foydalanuvchini yaratishga harakat qiling
            try:
                user = User(
                    username=username,
                    email=form.cleaned_data['email'],  # Emailni qo'shish
                    password=make_password(password1)  # Parolni shifrlash
                )
                user.save()
                
                # Email tasdiqlash kodi yuborish
                verification_code = str(random.randint(100000, 999999))  # 6 raqamli tasdiqlash kodi
                send_verification_email(request, user.email, verification_code)

                # Tasdiqlash kodini sessiyaga saqlash
                request.session['verification_code'] = verification_code
                request.session['user_email'] = user.email
                verification_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')  # datetime ni satrga aylantirish
                request.session['verification_time'] = verification_time

                messages.success(request, 'Ro\'yxatdan o\'tishingiz muvaffaqiyatli yakunlandi! Iltimos, emailni tekshiring.')

                # Javobda yuboriladigan datetime obyekti
                response_data = {
                    'status': 'success',
                    'message': 'Ro\'yxatdan o\'tish muvaffaqiyatli',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # datetime ni satrga aylantirish
                }
                return JsonResponse(response_data)
            except IntegrityError as e:
                messages.error(request, f'Foydalanuvchi yaratishda xatolik yuz berdi: {str(e)}')
                return JsonResponse({'status': 'error', 'message': 'Foydalanuvchi yaratishda xatolik yuz berdi.'})

    else:
        form = UserRegistrationForm()  # Bo'sh forma

    return render(request, 'user/register.html', {'form': form})


def is_password_strong(password):
    # Parol uchun murakkablik shartlari
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):  # Katta harf
        return False
    if not re.search(r"[a-z]", password):  # Kichik harf
        return False
    if not re.search(r"[0-9]", password):  # Raqam
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # Maxsus belgi
        return False
    return True

def verify_email(request):
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        expected_code = request.session.get('verification_code')
        verification_time = request.session.get('verification_time')

        if verification_time and timezone.now() - verification_time < timedelta(minutes=10):
            if verification_code == expected_code:
                messages.success(request, 'Sizning hisobingiz tasdiqlandi!')
                user_email = request.session.get('user_email')
                try:
                    user = User.objects.get(email=user_email)
                    user.email_verified = True
                    user.save()
                    del request.session['verification_code']
                    del request.session['user_email']
                    del request.session['verification_time']
                    return redirect('user:login')
                except User.DoesNotExist:
                    messages.error(request, 'Foydalanuvchi topilmadi.')
                    return redirect('user:register')
            else:
                messages.error(request, 'Noto\'g\'ri tasdiqlash kodi.')
        else:
            messages.error(request, 'Tasdiqlash kodi muddati o\'tgan.')

    return render(request, 'user/verify_email.html')

# Parolni tiklash uchun
class CustomPasswordResetView(PasswordResetView):
    template_name = 'user/password_reset_form.html'  # Parolni tiklash formasi
    email_template_name = 'user/password_reset_email.html'  # Email shabloni
    success_url = reverse_lazy('user:password_reset_done')  # Muvaffaqiyatli qabul qilish sahifasi
    form_class = PasswordResetForm  # Django standart parolni tiklash formasi


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'user/password_reset_done.html'  # Parolni tiklash muvaffaqiyati


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'user/password_reset_confirm.html'  # Parolni tiklash uchun tasdiqlash sahifasi
    success_url = reverse_lazy('user:password_reset_complete')  # Tasdiqlashdan so'ng sahifa


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'user/password_reset_complete.html'

# login_view
def login_view(request):
    next_url = request.GET.get('next')

    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Foydalanuvchini autentifikatsiya qilish
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('services:service_list')
            else:
                messages.error(request, 'Noto\‘g\‘ri login yoki parol.')
        else:
            messages.error(request, 'Noto‘g\‘ri login yoki parol.')
    else:
        form = UserLoginForm()

    return render(request, 'user/login.html', {'form': form})



def home(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Your account has been created successfully!")
            return redirect('home')
    else:
        form = UserCreationForm()

    steps = [
        {'title': "1-qadam: Ro'yxatdan o'ting", 'description': "Saytda ro'yxatdan o'ting va shaxsiy ma'lumotlaringizni kiriting.", 'icon': 'user-plus'},
        {'title': "2-qadam: Balansni to'ldiring", 'description': "Hisobingizni to'ldirib, xizmatlardan foydalanishga tayyorlaning.", 'icon': 'wallet'},
        {'title': "3-qadam: Xizmat tanlash", 'description': "Platformangizga mos keladigan xizmatni tanlang va tafsilotlarni ko'ring.", 'icon': 'shopping-cart'},
        {'title': "4-qadam: Buyurtma bering", 'description': "Tanlangan xizmatni to'lang va buyurtmani tasdiqlang.", 'icon': 'check-circle'}
    ]

    context = {
        'form': form,
        'steps': steps
    }
    return render(request, 'user/home.html', context)


def logout_view(request):

    logout(request)
    return redirect('user:home')
