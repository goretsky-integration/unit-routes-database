import models
from repositories.base import BaseRepository

__all__ = ('AccountRepository',)


class AccountRepository(BaseRepository):

    async def get_all(self, skip: int, limit: int) -> list[models.Account]:
        query = self._database.find({}, {'_id': 0}).skip(skip).limit(limit)
        return [models.Account.parse_obj(account) async for account in query]
