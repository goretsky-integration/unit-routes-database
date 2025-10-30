from django.contrib import admin
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _, gettext
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from telegram.models import TelegramChat, TelegramMessage
from user_roles.services import update_user_role


@admin.display(description=_('Status'))
def message_status(obj: TelegramMessage) -> str:
    if obj.sent_at:
        return gettext('Sent')
    if obj.error_message:
        return gettext('Error')
    return gettext('Pending')


class IsSentFilter(admin.SimpleListFilter):
    title = _('Sent status')
    parameter_name = 'is_sent'

    def lookups(self, request, model_admin):
        return (
            ('sent', _('Sent')),
            ('not_sent', _('Not Sent')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'sent':
            return queryset.exclude(sent_at__isnull=True)
        if self.value() == 'not_sent':
            return queryset.filter(sent_at__isnull=True)
        return queryset


class ErrorFilter(admin.SimpleListFilter):
    title = _('Error status')
    parameter_name = 'error_status'

    def lookups(self, request, model_admin):
        return (
            ('with_error', _('With Error')),
            ('without_error', _('Without Error')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'with_error':
            return queryset.exclude(error_message__isnull=True).exclude(
                error_message__exact='',
            )
        if self.value() == 'without_error':
            return queryset.filter(
                error_message__isnull=True,
            ) | queryset.filter(error_message__exact='')
        return queryset


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


@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = ('text', 'chat_id', 'to_be_sent_at', message_status)
    list_display_links = ('text', 'chat_id', 'to_be_sent_at')
    ordering = ('-to_be_sent_at',)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'chat_id',
                    'bot_token',
                    'text',
                    'media_file_ids',
                    'to_be_sent_at',
                    'reply_markup',
                )
            },
        ),
        (
            _('Success'),
            {
                'fields': (
                    'chat_message_ids',
                    'sent_at',
                )
            },
        ),
        (
            _('Error'),
            {
                'fields': (
                    'error_message',
                    'retries_count',
                ),
            },
        ),
    )
    list_filter = (IsSentFilter, ErrorFilter)
