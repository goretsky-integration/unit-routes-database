from django.contrib import admin

from telegram.models import TelegramChat


@admin.register(TelegramChat)
class TelegramChatAdmin(admin.ModelAdmin):
    list_filter = ('type', 'role')
    list_display = ('title', 'username', 'type', 'role', 'created_at')
    list_select_related = ('role',)
    readonly_fields = ('created_at', 'chat_id', 'type')
