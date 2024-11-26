from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'user'  # Namespace qo'shish

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('verify_email/', views.verify_email, name='verify_email'),

    # Parolni tiklash URL'lari
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
