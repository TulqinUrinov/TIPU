from django.contrib import admin
from .models import TgPost, BotUser


@admin.register(TgPost)
class TgPostAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "created_at")


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "username", "tg_name", "student")
