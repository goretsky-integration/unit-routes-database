import models
from repositories.base import BaseRepository

__all__ = (
    'ReportTypeRepository',
)


class ReportTypeRepository(BaseRepository):

    async def get_all(self, skip: int, limit: int) -> list[models.ReportType]:
        query = self._database.find({}).skip(skip).limit(limit)
        return [models.ReportType.parse_obj(report_type) async for report_type in query]
