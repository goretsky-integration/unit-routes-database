from django.core.management import BaseCommand
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from reports.models.report_routes import ReportRoute
from telegram.services import batch_create_telegram_messages
from write_offs.services import (
    get_upcoming_write_offs, get_write_off_status, format_write_off,
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        write_offs = get_upcoming_write_offs()
        for write_off in write_offs:
            status = get_write_off_status(write_off)
            if status is None:
                continue
            text = format_write_off(write_off, status)
            chat_ids = (
                ReportRoute.objects
                .filter(
                    report_type__name='WRITE_OFFS',
                    unit__uuid=write_off.unit.uuid,
                )
                .values_list('telegram_chat__chat_id', flat=True)
            )

            batch_create_telegram_messages(
                chat_ids=chat_ids,
                text=text,
                reply_markup=InlineKeyboardMarkup(
                    keyboard=[
                        [
                            InlineKeyboardButton(
                                text='🗑️ Ингредиент списан',
                                callback_data=f'write-off:{write_off.id.hex}'
                            )
                        ]
                    ]
                )
            )
            write_off.is_notification_sent = True
            write_off.save(update_fields=['is_notification_sent'])
