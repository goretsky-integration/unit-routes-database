import models
from repositories.base import BaseRepository

__all__ = (
    'UnitRepository',
)


class UnitRepository(BaseRepository):

    async def get_all(self, limit: int, skip: int) -> list[models.Unit]:
        query = self._database.find({}).skip(skip).limit(limit)
        return [models.Unit.parse_obj(unit) async for unit in query]

    async def get_by_region(self, region: str, limit: int, skip: int) -> list[models.Unit]:
        query = self._database.find({'region': region}).skip(skip).limit(limit)
        return [models.Unit.parse_obj(unit) async for unit in query]
