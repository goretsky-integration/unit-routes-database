import models
from repositories.base import BaseRepository

__all__ = (
    'StatisticsReportTypeRepository',
)


class StatisticsReportTypeRepository(BaseRepository):

    async def get_all(self, skip: int, limit: int) -> list[models.StatisticsReportType]:
        query = self._database.find({}).skip(skip).limit(limit)
        return [models.StatisticsReportType.parse_obj(report_type) async for report_type in query]
