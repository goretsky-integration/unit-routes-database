from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

import exceptions
import models
from db.models import TelegramChat
from repositories.base import BaseRepository

__all__ = ('TelegramChatRepository',)


class TelegramChatRepository(BaseRepository):

    def get_by_chat_id(self, *, chat_id: int) -> models.TelegramChat:
        statement = select(TelegramChat).where(TelegramChat.chat_id == chat_id)
        with self._session_factory() as session:
            result = session.execute(statement)
            telegram_chat = result.scalar()
        if telegram_chat is None:
            raise exceptions.DoesNotExistInDatabase('Telegram chat by this chat ID is not found')
        return models.TelegramChat(id=telegram_chat.id, chat_id=telegram_chat.chat_id, title=telegram_chat.title)

    def create(self, *, chat_id: int, title: str | None = None) -> models.TelegramChat:
        telegram_chat = TelegramChat(chat_id=chat_id, title=title)
        try:
            with self._session_factory() as session, session.begin():
                session.add(telegram_chat)
                session.flush()
        except IntegrityError:
            raise exceptions.AlreadyExistsInDatabase('Telegram chat by this chat ID already exists')
        return models.TelegramChat(id=telegram_chat.id, chat_id=telegram_chat.chat_id, title=telegram_chat.title)

    def get_or_create(self, *, chat_id: int, title: str | None = None) -> tuple[models.TelegramChat, bool]:
        try:
            return self.get_by_chat_id(chat_id=chat_id), False
        except exceptions.DoesNotExistInDatabase:
            return self.create(chat_id=chat_id, title=title), True
