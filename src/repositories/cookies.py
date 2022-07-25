import json

from utils import exceptions
from repositories.base import BaseRepository

__all__ = (
    'CookiesRepository',
)


class CookiesRepository(BaseRepository):

    async def get_by_account_name(self, account_name: str) -> str:
        cookies = await self._database.get(f'cookies_{account_name}')
        if cookies is None:
            raise exceptions.NoCookiesError
        return json.loads(cookies)
