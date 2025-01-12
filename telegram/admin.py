from django.contrib import admin
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from telegram.models import TelegramChat
from user_roles.services import update_user_role


class TelegramChatResource(ModelResource):
    class Meta:
        model = TelegramChat


@admin.register(TelegramChat)
class TelegramChatAdmin(ImportExportModelAdmin):
    resource_class = TelegramChatResource
    list_filter = ('type', 'role')
    list_display = ('title', 'username', 'type', 'role', 'created_at')
    list_select_related = ('role',)
    readonly_fields = ('created_at', 'chat_id', 'type')
    search_fields = ('title', 'username', 'chat_id',)
    search_help_text = capfirst(
        _('telegram|admin|telegram_chat|search_help_text')
    )

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj: TelegramChat, form, change):
        if obj.id is not None:
            telegram_chat = (
                TelegramChat.objects
                .select_related('role')
                .get(id=obj.id)
            )
            if telegram_chat.role != obj.role:
                update_user_role(user=telegram_chat, role=obj.role)
        super().save_model(request, obj, form, change)
