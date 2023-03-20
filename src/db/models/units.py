from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

__all__ = ('Unit', 'Region')


class Region(Base):
    __tablename__ = 'regions'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    units: Mapped[list['Unit']] = relationship('Unit', back_populates='region')


class Unit(Base):
    __tablename__ = 'units'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    uuid: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), unique=True, nullable=False)
    office_manager_account_name: Mapped[str] = mapped_column(String(64), nullable=False)
    dodo_is_api_account_name: Mapped[str] = mapped_column(String(64), nullable=False)
    region_id: Mapped[int] = mapped_column(ForeignKey('regions.id'), nullable=False)
    region: Mapped[Region] = relationship('Region', back_populates='units')
