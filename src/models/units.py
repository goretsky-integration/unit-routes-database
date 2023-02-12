from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel

__all__ = ('Unit', 'Region')


class Unit(BaseModel):
    id: int
    name: str
    uuid: UUID
    account_name: str
    region: str


@dataclass(frozen=True, slots=True)
class Region:
    id: int
    name: str
