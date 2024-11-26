from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Profil rasmi
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Telefon raqami
    bio = models.TextField(blank=True, null=True)  
    # username = models.CharField(max_length=150, unique=True, error_messages= {
    #         'max_length': 'The name cannot be longer than 100 characters.',
    #     })

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
