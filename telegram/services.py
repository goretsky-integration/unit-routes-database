from telegram.models import TelegramChat
from telegram.selectors import get_telegram_chats_by_chat_id


def update_telegram_chat(
        *,
        chat_id: int,
        title: str,
        username: str | None,
) -> int:
    telegram_chats = get_telegram_chats_by_chat_id(chat_id=chat_id)
    return telegram_chats.update(title=title, username=username)


def create_telegram_chat(
        *,
        chat_id: int,
        title: str,
        username: str | None,
        chat_type: TelegramChat.ChatType,
) -> TelegramChat:
    return TelegramChat.objects.create(
        chat_id=chat_id,
        title=title,
        username=username,
        type=chat_type,
    )
