from utils import exceptions
from repositories.base import BaseRepository

import models

__all__ = (
    'AccessTokenRepository',
)


class AccessTokenRepository(BaseRepository):

    async def get_by_account_name(self, account_name: str) -> models.Token:
        access_token = await self._database.get(f'token_{account_name}')
        if access_token is None:
            raise exceptions.NoTokenError
        return models.Token(access_token=access_token)
