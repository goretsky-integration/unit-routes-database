from db import mongo_db
from repositories import (
    CookiesRepository,
    TokensRepository,
    UnitRepository,
    ReportRepository,
    AccountRepository,
    ReportTypeRepository,
    StatisticsReportTypeRepository,
)

__all__ = (
    'get_reports_repository',
    'get_cookies_repository',
    'get_units_repository',
    'get_tokens_repository',
    'get_accounts_repository',
    'get_report_types_repository',
    'get_statistics_report_types_repository',
)


def get_tokens_repository() -> TokensRepository:
    return TokensRepository(mongo_db.tokens)


def get_cookies_repository() -> CookiesRepository:
    return CookiesRepository(mongo_db.cookies)


def get_units_repository() -> UnitRepository:
    return UnitRepository(mongo_db.units)


def get_reports_repository() -> ReportRepository:
    return ReportRepository(mongo_db.reports)


def get_accounts_repository() -> AccountRepository:
    return AccountRepository(mongo_db.accounts)


def get_report_types_repository() -> ReportTypeRepository:
    return ReportTypeRepository(mongo_db.report_types)


def get_statistics_report_types_repository() -> StatisticsReportTypeRepository:
    return StatisticsReportTypeRepository(mongo_db.statistics_report_types)
