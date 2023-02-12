from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.models.report_types import ReportType
from db.models.telegram_chats import TelegramChat
from db.models.units import Unit

__all__ = ('ReportRoute',)


class ReportRoute(Base):
    __tablename__ = 'report_routes'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_chat_id: Mapped[TelegramChat] = mapped_column(ForeignKey('telegram_chats.id'), nullable=False)
    report_type_id: Mapped[ReportType] = mapped_column(ForeignKey('report_types.id'), nullable=False)
    unit_id: Mapped[Unit] = mapped_column(ForeignKey('units.id'), nullable=False)

    telegram_chat: Mapped[TelegramChat] = relationship('TelegramChat')
    report_type: Mapped[ReportType] = relationship('ReportType')
    unit: Mapped[Unit] = relationship('Unit')

    __table_args__ = (UniqueConstraint('telegram_chat_id', 'report_type_id', 'unit_id'),)
