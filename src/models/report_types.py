from pydantic import BaseModel, Field

__all__ = (
    'ReportType',
    'StatisticsReportType',
)


class ReportType(BaseModel):
    id: int = Field(alias='_id')
    name: str
    verbose_name: str


class StatisticsReportType(BaseModel):
    id: int = Field(alias='_id')
    name: str
    verbose_name: str
