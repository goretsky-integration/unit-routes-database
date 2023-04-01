from django.db.models import QuerySet

from core.exceptions import NotFoundError
from reports.models.report_types import ReportType
from reports.models.report_routes import ReportRoute


def get_report_types() -> QuerySet[ReportType]:
    return ReportType.objects.all()


def get_report_type_by_name(name: str) -> ReportType:
    try:
        return ReportType.objects.get(name=name, is_active=True)
    except ReportType.DoesNotExist:
        raise NotFoundError('Report type is not found')


def filter_active_report_types(
        queryset: QuerySet[ReportType],
) -> QuerySet[ReportType]:
    return queryset.filter(is_active=True)


def filter_statistics_report_types(
        queryset: QuerySet[ReportType],
) -> QuerySet[ReportType]:
    return queryset.filter(parent__name='STATISTICS')


def exclude_statistics_report_types(
        queryset: QuerySet[ReportType],
) -> QuerySet[ReportType]:
    return queryset.exclude(parent__name='STATISTICS')


def get_active_report_types(*, limit: int, offset: int) -> QuerySet[ReportType]:
    return exclude_statistics_report_types(
        filter_active_report_types(get_report_types())
    )[offset:limit + offset]


def get_active_statistics_report_types(
        *,
        limit: int,
        offset: int,
) -> QuerySet[ReportType]:
    return filter_statistics_report_types(
        filter_active_report_types(get_report_types())
    )[offset:limit + offset]


def get_report_type_by_id(report_type_id: int) -> ReportType:
    try:
        return ReportType.objects.get(id=report_type_id)
    except ReportType.DoesNotExist:
        raise NotFoundError('Report type by ID is not found')


def get_report_routes() -> QuerySet[ReportRoute]:
    return ReportRoute.objects.all()


def filter_report_routes_by_chat_id(
        *,
        queryset: QuerySet[ReportRoute],
        chat_id,
) -> QuerySet[ReportRoute]:
    return queryset.filter(telegram_chat__chat_id=chat_id)


def filter_report_routes_by_report_type_id(
        *,
        queryset: QuerySet[ReportRoute],
        report_type_id: int,
) -> QuerySet[ReportRoute]:
    return queryset.filter(report_type_id=report_type_id)


def filter_report_routes_by_unit_id(
        *,
        queryset: QuerySet[ReportRoute],
        unit_id: int,
) -> QuerySet[ReportRoute]:
    return queryset.filter(unit_id=unit_id)


def get_report_routes_by_report_type_id_and_chat_id(
        *,
        report_type_id: int,
        chat_id: int,
        limit: int,
        offset: int,
) -> QuerySet[ReportRoute]:
    report_routes = get_report_routes().select_related('telegram_chat')
    return filter_report_routes_by_report_type_id(
        queryset=filter_report_routes_by_chat_id(
            queryset=report_routes,
            chat_id=chat_id,
        ),
        report_type_id=report_type_id,
    )[offset:limit + offset]


def get_report_routes_by_report_type_id_and_unit_id(
        *,
        report_type_id: int,
        unit_id: int,
        limit: int,
        offset: int,
) -> QuerySet[ReportRoute]:
    report_routes = get_report_routes().select_related('telegram_chats')
    return filter_report_routes_by_report_type_id(
        queryset=filter_report_routes_by_unit_id(
            queryset=report_routes,
            unit_id=unit_id,
        ),
        report_type_id=report_type_id,
    )[offset:limit + offset]
