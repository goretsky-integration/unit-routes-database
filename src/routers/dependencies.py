from db import redis_db, mongo_db
from repositories import (
    CookiesRepository,
    AccessTokenRepository,
    UnitRepository,
    ReportRepository,
    AccountRepository,
)

__all__ = (
    'get_reports_repository',
    'get_cookies_repository',
    'get_units_repository',
    'get_access_tokens_repository',
    'get_accounts_repository',
)


def get_access_tokens_repository() -> AccessTokenRepository:
    return AccessTokenRepository(redis_db.connection)


def get_cookies_repository() -> CookiesRepository:
    return CookiesRepository(redis_db.connection)


def get_units_repository() -> UnitRepository:
    return UnitRepository(mongo_db.units)


def get_reports_repository() -> ReportRepository:
    return ReportRepository(mongo_db.reports)


def get_accounts_repository() -> AccountRepository:
    return AccountRepository(mongo_db.accounts)
