# schema.py faylida
import graphene
from .models import PlatformToken
from graphene_django.types import DjangoObjectType

# PlatformToken modelining GraphQL turini yaratish
class PlatformTokenType(DjangoObjectType):
    class Meta:
        model = PlatformToken
        fields = ("id", "platform_name", "token", "created_at")

# Platform tokenlarini olish uchun query
class Query(graphene.ObjectType):
    platform_tokens = graphene.List(PlatformTokenType)

    def resolve_platform_tokens(root, info):
        user = info.context.user
        # Faqat admin foydalanuvchilar uchun tokenlarni olish imkonini berish
        if user.is_authenticated and user.is_superuser:
            return PlatformToken.objects.all()  # Administratorlar barcha tokenlarni oladi
        # Agar foydalanuvchi autentifikatsiya qilingan, lekin admin emas, hech narsa qaytarmaslik
        return None  # Yoki return [] - agar siz bo'sh ro'yxatni qaytarishni xohlasangiz

# Platform tokenini o‘rnatish uchun mutation
class AddPlatformToken(graphene.Mutation):
    class Arguments:
        platform_name = graphene.String(required=True)
        token = graphene.String(required=True)

    platform_token = graphene.Field(PlatformTokenType)

    def mutate(self, info, platform_name, token):
        user = info.context.user
        # Faqat admin foydalanuvchilar uchun token qo'shish imkonini berish
        if user.is_authenticated and user.is_superuser:
            if platform_name in ['YouTube', 'Instagram', 'Telegram']:
                platform_token, created = PlatformToken.objects.update_or_create(
                    user=user, platform_name=platform_name,
                    defaults={'token': token}
                )
                return AddPlatformToken(platform_token=platform_token)
            else:
                raise Exception("Only SMM platform tokens can be added.")
        raise Exception("Authentication required or insufficient permissions.")

# Mutationlarni asosiy schema-ga qo‘shish
class Mutation(graphene.ObjectType):
    add_platform_token = AddPlatformToken.Field()

# Asosiy schema yaratish
schema = graphene.Schema(query=Query, mutation=Mutation)
