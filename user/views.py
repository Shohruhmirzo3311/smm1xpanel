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
from django.utils.dateparse import parse_datetime


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
            email = form.cleaned_data['email']

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Bu foydalanuvchi nomi allaqachon mavjud. Iltimos, boshqa nom tanlang.')
                return render(request, 'user/register.html', {'form': form})

            try:
                user = User(username=username, email=email, password=make_password(password1))
                user.save()
                
                verification_code = str(random.randint(100000, 999999))
                send_verification_email(request, user.email, verification_code)

                request.session['verification_code'] = verification_code
                request.session['user_email'] = user.email
                request.session['verification_time'] = timezone.now().isoformat()

                messages.success(request, 'Ro\'yxatdan o\'tishingiz muvaffaqiyatli yakunlandi! Iltimos, emailni tekshiring.')
                return JsonResponse({'status': 'success', 'message': 'Ro\'yxatdan o\'tish muvaffaqiyatli'})
            except IntegrityError as e:
                messages.error(request, f'Foydalanuvchi yaratishda xatolik yuz berdi: {str(e)}')

    else:
        form = UserRegistrationForm()
    return render(request, 'user/register.html', {'form': form})



def verify_email(request):
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        expected_code = request.session.get('verification_code')
        verification_time = request.session.get('verification_time')

        if verification_time:
            verification_time = parse_datetime(verification_time)

            # Tasdiqlash kodi to‘g‘ri va vaqti o‘tmaganligini tekshirish
            if verification_code == expected_code and timezone.now() - verification_time < timedelta(minutes=10):
                messages.success(request, 'Sizning hisobingiz tasdiqlandi!')
                user_email = request.session.get('user_email')
                try:
                    user = User.objects.get(email=user_email)
                    user.email_verified = True
                    user.save()
                    del request.session['verification_code']
                    del request.session['user_email']
                    del request.session['verification_time']
                    return redirect('services:service_list')  # Bu yerda to‘g‘ri URLdan foydalaning
                except User.DoesNotExist:
                    messages.error(request, 'Foydalanuvchi topilmadi.')
            else:
                messages.error(request, 'Tasdiqlash kodi noto‘g‘ri yoki muddati o‘tgan.')
    return render(request, 'user/verify_email.html')

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
                return redirect( 'services:service_list')
            else:
                messages.error(request, 'Noto\‘g\‘ri login yoki parol.')
        else:
            messages.error(request, 'Noto‘g\‘ri login yoki parol.')
    else:
        form = UserLoginForm()

    return render(request, 'user/login.html', {'form': form})



from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

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

    faqs = [
        {'question': 'Xizmatlaringiz qanday?', 'answer': 'Biz Telegram, Instagram, YouTube va boshqa platformalar uchun sifatli SMM xizmatlarini taklif etamiz.'},
        {'question': 'Qanday qilib ro‘yxatdan o‘tishim mumkin?', 'answer': 'Siz "Ro\'yxatdan o\'tish" tugmasini bosish orqali ro\'yxatdan o\'tishingiz mumkin.'},
        {'question': 'Xizmatlardan qanday foydalanish mumkin?', 'answer': 'Xizmatlar sahifasidan tanlangan xizmatni tanlang va buyurtma bering.'},
        {'question': 'Mening buyurtmamni qanday kuzatishim mumkin?', 'answer': 'Siz buyurtma berishdan so‘ng, elektron pochta orqali kuzatish raqamini olasiz.'},
        {'question': 'To‘lov usullari qanday?', 'answer': 'Biz bir nechta to‘lov usullarini qo‘llab-quvvatlaymiz, ularni to‘lov sahifasida ko‘rishingiz mumkin.'},
        {'question': 'Qanday yordam olsam bo‘ladi?', 'answer': 'Biz bilan bog‘laning, biz sizga yordam berishga tayyormiz!'},
        {'question': 'Xizmatlar narxi qanday belgilangan?', 'answer': 'Xizmatlar narxi xizmatning murakkabligi va talablarga qarab belgilangan.'},
        {'question': 'Buyurtmalarim qachon bajariladi?', 'answer': 'Buyurtma berishdan so‘ng, sizga bajarish muddati to‘g‘risida ma\'lumot beriladi.'},
        {'question': 'Agar xizmatdan mamnun bo‘lmasam nima qilishim kerak?', 'answer': 'Iltimos, biz bilan bog‘laning va muammoni hal qilishga harakat qilamiz.'},
        {'question': 'Qanday qilib balansimni to‘ldirishim mumkin?', 'answer': 'Balansni to‘ldirish uchun to‘lov sahifasiga o‘ting va kerakli summani kiriting.'},
        {'question': 'Savollarim bo‘lsa, qanday bog‘lanishim mumkin?', 'answer': 'Biz bilan telefon yoki elektron pochta orqali bog‘lanishingiz mumkin.'},
        {'question': 'Qanday qilib parolimni tiklashim mumkin?', 'answer': 'Login sahifasida "Parolni tiklash" opsiyasini tanlang va ko\'rsatmalarga amal qiling.'},
    ]

    context = {
        'form': form,
        'steps': steps,
        'faqs': faqs  # FAQ ro'yxatini konteksta qo'shamiz
    }
    return render(request, 'user/home.html', context)


def logout_view(request):

    logout(request)
    return redirect('user:home')
