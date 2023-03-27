from django.contrib import admin

from telegram.models import TelegramChat


@admin.register(TelegramChat)
class TelegramChatAdmin(admin.ModelAdmin):
    list_filter = ('type',)
