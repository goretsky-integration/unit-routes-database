from collections.abc import Iterable

from django.db.utils import IntegrityError

from core.exceptions import AlreadyExistsError
from reports.models.report_routes import ReportRoute
from reports.selectors import (
    get_report_routes,
    filter_report_routes_by_report_type_id,
    filter_report_routes_by_chat_id,
)


def create_report_routes(
        *,
        telegram_chat_id: int,
        report_type_id: int,
        unit_ids: Iterable[int],
) -> list[ReportRoute]:
    report_routes = [
        ReportRoute(
            unit_id=unit_id,
            telegram_chat_id=telegram_chat_id,
            report_type_id=report_type_id,
        ) for unit_id in unit_ids
    ]
    try:
        return ReportRoute.objects.bulk_create(report_routes)
    except IntegrityError:
        raise AlreadyExistsError('Unit route already exists')


def delete_report_routes(
        *,
        chat_id: int,
        report_type_id: int,
        unit_ids: Iterable[int],
) -> int:
    report_routes = filter_report_routes_by_chat_id(
        queryset=filter_report_routes_by_report_type_id(
            queryset=get_report_routes(),
            report_type_id=report_type_id,
        ),
        chat_id=chat_id,
    ).filter(unit_id__in=unit_ids)
    deleted_rows_count, _ = report_routes.delete()
    return deleted_rows_count
