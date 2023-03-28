from django.db.models import QuerySet

from core.exceptions import NotFoundError
from reports.models.report_types import ReportType


def get_report_types(*, limit: int, offset: int) -> QuerySet[ReportType]:
    return ReportType.objects.all()[offset:limit + offset]


def get_active_report_types(*, limit: int, offset: int) -> QuerySet[ReportType]:
    return get_report_types(limit=limit, offset=offset).filter(is_active=True)


def get_active_statistics_report_types(
        *,
        limit: int,
        offset: int,
) -> QuerySet[ReportType]:
    return get_active_report_types(
        limit=limit,
        offset=offset,
    ).filter(parent__name='STATISTICS')


def get_report_type_by_id(report_type_id: int) -> ReportType:
    try:
        return ReportType.objects.get(id=report_type_id)
    except ReportType.DoesNotExist:
        raise NotFoundError('Report type by ID is not found')
