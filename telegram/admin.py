from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.text import capfirst

from telegram.models import TelegramChat


@admin.register(TelegramChat)
class TelegramChatAdmin(admin.ModelAdmin):
    list_filter = ('type', 'role')
    list_display = ('title', 'username', 'type', 'role', 'created_at')
    list_select_related = ('role',)
    readonly_fields = ('created_at', 'chat_id', 'type')
    search_fields = ('title', 'username', 'chat_id',)
    search_help_text = capfirst(
        _('telegram|admin|telegram_chat|search_help_text')
    )
