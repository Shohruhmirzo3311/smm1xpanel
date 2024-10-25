from django.db import models
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

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
    name = models.CharField(max_length=100)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='YouTube')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Kategoriya bilan bog'lash
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    completion_time = models.IntegerField()  # daqiqalarda

    def save(self, *args, **kwargs):
        # Narxni 30% foyda bilan hisoblash
        self.price = self.base_price * 1.3
        if not self.completion_time:
            self.completion_time = 60
        super().save(*args, **kwargs)

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
        super().save(*args, **kwargs)

    def time_left(self):
        remaining_time = self.expected_completion_time - timezone.now()
        return remaining_time if remaining_time.total_seconds() > 0 else timedelta(0)

    def __str__(self):
        return f"Order by {self.user.username} for {self.service.name}"
