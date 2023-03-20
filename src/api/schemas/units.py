from typing import TypeAlias
from uuid import UUID

from pydantic import BaseModel, PositiveInt, constr, Field

__all__ = ('Unit', 'Region', 'RegionCreate', 'UnitID')

UnitID: TypeAlias = PositiveInt


class Unit(BaseModel):
    id: PositiveInt = Field(
        description='Legacy unit\'s iD',
    )
    name: constr(min_length=1, max_length=64)
    uuid: UUID = Field(
        description='It\'s preferred to use UUID over int ID',
    )
    office_manager_account_name: constr(min_length=1, max_length=64) = Field(
        description='Unit authentication in Dodo API related to this account',
    )
    dodo_is_api_account_name: constr(min_length=1, max_length=64) = Field()
    region: constr(min_length=1, max_length=64) = Field(
        description='Region which unit is related to',
    )


class RegionCreate(BaseModel):
    name: constr(min_length=1, max_length=64)


class Region(BaseModel):
    id: PositiveInt
    name: constr(min_length=1, max_length=64)
