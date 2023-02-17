from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base

__all__ = ('TelegramChat',)


class TelegramChat(Base):
    __tablename__ = 'telegram_chats'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
