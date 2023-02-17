from pydantic import BaseModel, PositiveInt, Field

from api.schemas.report_types import ReportTypeName

__all__ = ('ReportRoute',)


class ReportRoute(BaseModel):
    report_type: ReportTypeName
    chat_id: int
    unit_ids: set[PositiveInt] = Field(min_items=1, max_items=30)
