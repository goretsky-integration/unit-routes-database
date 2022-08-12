import models
from repositories.base import BaseRepository
from utils import exceptions

__all__ = (
    'CookiesRepository',
)


class CookiesRepository(BaseRepository):

    async def get_by_account_name(self, account_name: str) -> models.AuthCookies:
        cookies = await self._database.find_one({'account_name': account_name}, {'_id': 0})
        if cookies is None:
            raise exceptions.NoCookiesError
        return models.AuthCookies.parse_obj(cookies)

    async def update(self, cookies_in: models.AuthCookies):
        query = {'account_name': cookies_in.account_name}
        update = {'$set': {'cookies': cookies_in.cookies}}
        await self._database.update_one(query, update, upsert=True)
