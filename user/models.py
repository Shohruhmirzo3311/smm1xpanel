from django.contrib.auth.models import AbstractUser
from django.db import models

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
