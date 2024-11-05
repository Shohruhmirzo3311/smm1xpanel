from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)  # Tasdiqlanganligini aniqlash uchun maydon
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Profil rasmi
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Telefon raqami
    bio = models.TextField(blank=True, null=True)  # Foydalanuvchi haqida ma'lumot

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']  # Foydalanuvchilarni username bo‘yicha tartiblash


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    additional_info = models.CharField(max_length=255, blank=True)  # Qo'shimcha ma'lumot uchun

    def __str__(self):
        return f"{self.user} profili"
