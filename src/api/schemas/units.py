from typing import TypeAlias
from uuid import UUID

from pydantic import BaseModel, PositiveInt, constr

__all__ = ('Unit', 'Region', 'RegionCreate', 'UnitID')

UnitID: TypeAlias = PositiveInt


class Unit(BaseModel):
    id: PositiveInt
    name: constr(min_length=1, max_length=64)
    uuid: UUID
    account_name: constr(min_length=1, max_length=64)
    region: constr(min_length=1, max_length=64)


class RegionCreate(BaseModel):
    name: constr(min_length=1, max_length=64)


class Region(BaseModel):
    id: PositiveInt
    name: constr(min_length=1, max_length=64)
