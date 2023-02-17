from db.engine import session_factory
from repositories import (
    UnitRepository,
    RegionRepository,
    ReportTypeRepository,
    ReportRouteRepository,
    TelegramChatRepository,
)

__all__ = (
    'get_units_repository',
    'get_regions_repository',
    'get_report_types_repository',
    'get_report_routes_repository',
    'get_telegram_chats_repository',
)


def get_units_repository() -> UnitRepository:
    return UnitRepository(session_factory)


def get_regions_repository() -> RegionRepository:
    return RegionRepository(session_factory)


def get_report_types_repository() -> ReportTypeRepository:
    return ReportTypeRepository(session_factory)


def get_report_routes_repository() -> ReportRouteRepository:
    return ReportRouteRepository(session_factory)


def get_telegram_chats_repository() -> TelegramChatRepository:
    return TelegramChatRepository(session_factory)
