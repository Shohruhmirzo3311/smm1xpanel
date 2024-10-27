from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
import decimal
import requests
from django.conf import settings


User = get_user_model()

# Foydalanuvchi balans modeli
class UserBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} balansi: {self.balance}"

    def update_balance(self, amount):
        self.balance += decimal.Decimal(amount)
        self.save()
    
    def has_sufficient_balance(self, amount):
        return self.balance >= decimal.Decimal(amount)



# Kategoriya modeli
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Service(models.Model):
    PLATFORM_CHOICES = [
        ('YouTube', 'YouTube'),
        ('Instagram', 'Instagram'),
        ('Telegram', 'Telegram'),
    ]

    SERVICE_TYPES = [
    # Umumiy xizmatlar
    ('like', 'Like'),
    ('comment', 'Comment'),
    ('follow', 'Follow'),
    ('share', 'Share'),
    ('view', 'View'),
    ('save', 'Save'),
    ('vote', 'Vote'),
    ('premium_like', 'Premium Like'),
    ('premium_comment', 'Premium Comment'),
    ('premium_follow', 'Premium Follow'),
    ('premium_share', 'Premium Share'),
    ('premium_view', 'Premium View'),

    # YouTube xizmatlari
    ('youtube_subscribe', 'YouTube Subscribe'),
    ('youtube_like', 'YouTube Like'),
    ('youtube_dislike', 'YouTube Dislike'),
    ('youtube_comment', 'YouTube Comment'),
    ('youtube_view', 'YouTube View'),
    ('youtube_share', 'YouTube Share'),
    ('youtube_watch_time', 'YouTube Watch Time'),
    ('youtube_premium_subscribe', 'YouTube Premium Subscribe'),
    ('youtube_premium_like', 'YouTube Premium Like'),
    ('youtube_premium_comment', 'YouTube Premium Comment'),
    ('youtube_premium_view', 'YouTube Premium View'),
    ('youtube_recommend', 'YouTube Recommend'),
    ('youtube_trending', 'YouTube Trending'),
    ('youtube_watch_complete', 'YouTube Watch Complete'),
    ('youtube_ads_view', 'YouTube Ads View'),
    ('youtube_super_chat', 'YouTube Super Chat'),
    ('youtube_super_sticker', 'YouTube Super Sticker'),
    ('youtube_channel_follow', 'YouTube Channel Follow'),
    ('youtube_live_view', 'YouTube Live View'),
    ('youtube_live_reaction', 'YouTube Live Reaction'),
    ('youtube_live_comment', 'YouTube Live Comment'),
    ('youtube_live_share', 'YouTube Live Share'),

    # Instagram xizmatlari
    ('instagram_follow', 'Instagram Follow'),
    ('instagram_like', 'Instagram Like'),
    ('instagram_comment', 'Instagram Comment'),
    ('instagram_share', 'Instagram Share'),
    ('instagram_story_view', 'Instagram Story View'),
    ('instagram_reel_view', 'Instagram Reel View'),
    ('instagram_save', 'Instagram Save'),
    ('instagram_igtv_view', 'Instagram IGTV View'),
    ('instagram_direct_message', 'Instagram Direct Message'),
    ('instagram_live_view', 'Instagram Live View'),
    ('instagram_live_comment', 'Instagram Live Comment'),
    ('instagram_live_like', 'Instagram Live Like'),
    ('instagram_live_reaction', 'Instagram Live Reaction'),
    ('instagram_premium_follow', 'Instagram Premium Follow'),
    ('instagram_premium_like', 'Instagram Premium Like'),
    ('instagram_premium_comment', 'Instagram Premium Comment'),
    ('instagram_premium_share', 'Instagram Premium Share'),
    ('instagram_premium_story_view', 'Instagram Premium Story View'),
    ('instagram_poll_vote', 'Instagram Poll Vote'),
    ('instagram_custom_comments', 'Instagram Custom Comments'),
    ('instagram_profile_visit', 'Instagram Profile Visit'),
    ('instagram_post_reach', 'Instagram Post Reach'),
    ('instagram_profile_impression', 'Instagram Profile Impression'),
    ('instagram_save_to_collection', 'Instagram Save to Collection'),

    # Telegram xizmatlari
    ('telegram_member', 'Telegram Member'),
    ('telegram_view', 'Telegram View'),
    ('telegram_post_share', 'Telegram Post Share'),
    ('telegram_vote', 'Telegram Vote'),
    ('telegram_comment', 'Telegram Comment'),
    ('telegram_reaction', 'Telegram Reaction'),
    ('telegram_forward', 'Telegram Forward'),
    ('telegram_poll_vote', 'Telegram Poll Vote'),
    ('telegram_premium_member', 'Telegram Premium Member'),
    ('telegram_premium_view', 'Telegram Premium View'),
    ('telegram_post_like', 'Telegram Post Like'),
    ('telegram_channel_subscriber', 'Telegram Channel Subscriber'),
    ('telegram_group_join', 'Telegram Group Join'),
    ('telegram_bot_interaction', 'Telegram Bot Interaction'),
    ('telegram_message_forward', 'Telegram Message Forward'),
    ('telegram_sticker_share', 'Telegram Sticker Share'),
    ('telegram_pinned_message', 'Telegram Pinned Message'),
    ('telegram_voice_message', 'Telegram Voice Message'),
    ('telegram_video_message', 'Telegram Video Message'),
    ('telegram_live_view', 'Telegram Live View'),
    ('telegram_live_reaction', 'Telegram Live Reaction'),
    ('telegram_live_comment', 'Telegram Live Comment'),
    ('telegram_live_share', 'Telegram Live Share'),
    ]

# Modelda foydalanish uchun:
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES, default='follow')
    name = models.CharField(max_length=100)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='YouTube')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Kategoriya bilan bog'lash
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    completion_time = models.IntegerField()  # daqiqalarda
    completion_rate = models.IntegerField(default=50000)  # kuniga maksimal bajarilish miqdori

    def save(self, *args, **kwargs):
        # Narxni 30% foyda bilan hisoblash
        self.price = self.base_price * 1.3
        if not self.completion_time:
            self.completion_time = 60
        super().save(*args, **kwargs)
    
    def update_price(self):
        """
        Narxni tashqi API orqali yangilash funksiyasi.
        """
        # Tashqi API URL manzili va kerakli parametrlar
        api_url = "https://api.example.com/get_service_price"
        params = {
            'service_name': self.name,
            'platform': self.platform,
            'category': self.category.name,
        }
        headers = {
            'Authorization': f"Bearer {settings.EXTERNAL_API_TOKEN}",
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(api_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            # API'dan narxni olish
            new_base_price = decimal.Decimal(data.get("base_price"))
            profit_margin = decimal.Decimal('1.3')  # 30% foyda

            # Narxni yangilash
            self.base_price = new_base_price
            self.price = new_base_price * profit_margin
            self.save()

        except requests.RequestException as e:
            print(f"API so'rovda xato yuz berdi: {e}")
        except (TypeError, ValueError) as e:
            print(f"API javobida kutilmagan qiymat: {e}")


    def __str__(self):
        return f"{self.name} ({self.platform})"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expected_completion_time = models.DateTimeField()
    is_completed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expected_completion_time:
            self.expected_completion_time = timezone.now() + timedelta(minutes=self.service.completion_time)

        user_balance = UserBalance.objects.get(user=self.user)
        if user_balance.has_sufficient_balance(self.service.price):
            user_balance.update_balance(-self.service.price)
            super().save(*args, **kwargs)
        else:
            raise ValueError("Yetarli balans mavjud emas")

    def time_left(self):
        remaining_time = self.expected_completion_time - timezone.now()
        return remaining_time if remaining_time.total_seconds() > 0 else timedelta(0)

    def __str__(self):
        return f"Order by {self.user.username} for {self.service.name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"


class PaymentMethod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)  # karta raqami
    expiry_date = models.CharField(max_length=5)  # MM/YY formatida
    cvv = models.CharField(max_length=3)

    def __str__(self):
        return f"{self.user.username} - Karta: {self.card_number}"


class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - {self.amount} so'm"


# Yana bir model qo'shilishi mumkin, masalan, cyber attackdan himoyalanish
class SecuritySettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_two_factor_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} xavfsizlik sozlamalari"