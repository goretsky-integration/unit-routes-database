from typing import TypeAlias

from pydantic import BaseModel, PositiveInt, constr

__all__ = ('ReportType', 'ReportTypeName', 'ReportTypeCreate')

ReportTypeName: TypeAlias = constr(min_length=1, max_length=64)


class ReportType(BaseModel):
    id: PositiveInt
    name: ReportTypeName
    verbose_name: ReportTypeName


class ReportTypeCreate(BaseModel):
    name: ReportTypeName
    verbose_name: ReportTypeName
