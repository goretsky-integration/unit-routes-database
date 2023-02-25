from typing import TypeAlias

from pydantic import BaseModel, constr

__all__ = (
    'TelegramChatTitle',
    'TelegramChat',
    'TelegramChatToUpdate',
    'TelegramChatsListPage',
)

TelegramChatTitle: TypeAlias = constr(min_length=1, max_length=255)


class TelegramChat(BaseModel):
    title: TelegramChatTitle | None
    chat_id: int


class TelegramChatToUpdate(BaseModel):
    title: TelegramChatTitle | None


class TelegramChatsListPage(BaseModel):
    telegram_chats: list[TelegramChat]
    is_end_of_list_reached: bool
