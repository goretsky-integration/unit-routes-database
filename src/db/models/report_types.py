from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

__all__ = ('ReportType',)


class ReportType(Base):
    __tablename__ = 'report_types'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    verbose_name: Mapped[str] = mapped_column(String(64), nullable=False)
    parent_id: Mapped[int] = mapped_column(ForeignKey('report_types.id'), nullable=True)
    parent: Mapped['ReportType'] = relationship('ReportType', remote_side=[id])
