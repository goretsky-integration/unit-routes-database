from db import redis_db
from repositories import (
    CookiesRepository,
    AccessTokenRepository,
)


def get_access_tokens_repository() -> AccessTokenRepository:
    return AccessTokenRepository(redis_db.connection)


def get_cookies_repository() -> CookiesRepository:
    return CookiesRepository(redis_db.connection)
