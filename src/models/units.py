from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

__all__ = (
    'Region',
    'Unit',
)


class Region(str, Enum):
    MOSCOW_4 = 'Москва 4'
    SMOLUGA = 'Смолуга'


class Unit(BaseModel):
    id: int = Field(alias='_id')
    name: str
    uuid: UUID
    account_name: str
    region: Region
