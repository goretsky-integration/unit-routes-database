from utils import exceptions
from repositories.base import BaseRepository

import models

__all__ = (
    'TokensRepository',
)


class TokensRepository(BaseRepository):

    async def get_by_account_name(self, account_name: str) -> models.Token:
        tokens = await self._database.find_one({'account_name': account_name}, {'_id': 0, 'refresh_token': 0})
        if tokens is None:
            raise exceptions.NoTokenError
        return models.Token.parse_obj(tokens)

    async def update(self, tokens_in: models.Token):
        query = {'account_name': tokens_in.account_name}
        update = {'$set': {'access_token': tokens_in.access_token, 'refresh_token': tokens_in.refresh_token}}
        await self._database.update_one(query, update, upsert=True)
