import random
import smtplib  # Email yuborish uchun
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

def send_verification_email(user_email, verification_code):
    subject = "Email Tasdiqlash"
    message = f"Sizning tasdiqlash kodingiz: {verification_code}"
    full_email = f"Subject: {subject}\n\n{message}"

    # Email yuborish
    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(settings.EMAIL_HOST_USER, user_email, full_email)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            verification_code = str(random.randint(100000, 999999))  # 6 raqamli tasdiqlash kodi
            send_verification_email(user.email, verification_code)
            # Tasdiqlash kodini saqlash uchun
            request.session['verification_code'] = verification_code  
            request.session['user_email'] = user.email  
            messages.success(request, "Ro'yxatdan o'tish muvaffaqiyatli bo'ldi! Emailingizni tasdiqlang.")
            return redirect('verify_email')  # Tasdiqlash sahifasiga o'tish
    else:
        form = UserRegistrationForm()
    return render(request, 'user/register.html', {'form': form})


def verify_email(request):
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        expected_code = request.session.get('verification_code')  # Sessiyadan tasdiqlash kodini olish

        if verification_code == expected_code:  # Kodni tekshirish
            messages.success(request, 'Sizning hisobingiz tasdiqlandi!')
            
            # Bu yerda foydalanuvchining emailini tasdiqlash yoki hisob holatini yangilash logikasini qo'shishingiz mumkin.
            user = request.user  # Tizimga kirgan foydalanuvchi
            user.email_verified = True  # Masalan, email tasdiqlanganligini yangilang
            user.save()  # O'zgarishlarni saqlang
            
            return redirect('login')  # Tasdiqlashdan so'ng login sahifasiga o'ting
        else:
            messages.error(request, 'Noto\'g\'ri tasdiqlash kodi.')
    
    return render(request, 'user/verify_email.html')  # Tasdiqlash sahifasini ko'rsatish

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

def login_view(request):
    next_url = request.GET.get('next', 'service_list')  # default url
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if form.cleaned_data.get('remember_me'):
                request.session.set_expiry(1209600)  # 2 hafta davomida sessiya
            else:
                request.session.set_expiry(0)  # Brauzer yopilganda sessiya tugaydi

            return redirect(next_url)  # Foydalanuvchini 'next' parametriga yo'naltiring
    else:
        form = UserLoginForm()
    return render(request, 'user/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')
