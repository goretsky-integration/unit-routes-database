from enum import Enum
from typing import Iterable

from pydantic import BaseModel, validator

__all__ = (
    'Report',
    'ReportType',
    'ReportChatIdAndUnitIds',
)


class ReportType(str, Enum):
    STATISTICS = 'STATISTICS'
    INGREDIENTS_STOP_SALES = 'INGREDIENTS_STOP_SALES'
    STREET_STOP_SALES = 'STREET_STOP_SALES'
    SECTOR_STOP_SALES = 'SECTOR_STOP_SALES'
    PIZZERIA_STOP_SALES = 'PIZZERIA_STOP_SALES'
    STOPS_AND_RESUMES = 'STOPS_AND_RESUMES'
    CANCELED_ORDERS = 'CANCELED_ORDERS'
    CHEATED_PHONE_NUMBERS = 'CHEATED_PHONE_NUMBERS'
    WRITE_OFFS = 'WRITE_OFFS'


class Report(BaseModel):
    report_type: ReportType
    chat_id: int
    unit_ids: list[int]


class ReportChatIdAndUnitIds(BaseModel):
    chat_id: int
    unit_ids: list[int]
