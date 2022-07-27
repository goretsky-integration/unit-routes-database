from utils import exceptions
from repositories.base import BaseRepository

import models

__all__ = (
    'AccessTokenRepository',
)


class AccessTokenRepository(BaseRepository):

    async def get_by_account_name(self, account_name: str) -> models.Token:
        tokens = await self._database.find_one({'account_name': account_name}, {'_id': 0, 'refresh_token': 0})
        if tokens is None:
            raise exceptions.NoTokenError
        return models.Token.parse_obj(tokens)
