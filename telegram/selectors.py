from django.db.models import QuerySet

from telegram.models import TelegramChat


def get_telegram_chats(*, limit: int, offset: int) -> QuerySet[TelegramChat]:
    return TelegramChat.objects.all()[offset:offset + limit]


def get_telegram_chats_by_chat_id(chat_id: int) -> QuerySet[TelegramChat]:
    return TelegramChat.objects.filter(chat_id=chat_id)
