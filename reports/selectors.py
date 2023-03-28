from django.db.models import QuerySet

from core.exceptions import NotFoundError
from reports.models.report_types import ReportType

def get_report_types() -> QuerySet[ReportType]:
    return ReportType.objects.all()


def filter_active_report_types(
        queryset: QuerySet[ReportType],
) -> QuerySet[ReportType]:
    return queryset.filter(is_active=True)


def get_active_report_types(*, limit: int, offset: int) -> QuerySet[ReportType]:
    return filter_active_report_types(get_report_types())[offset:limit + offset]


def get_active_statistics_report_types(
        *,
        limit: int,
        offset: int,
) -> QuerySet[ReportType]:
    return (
        filter_active_report_types(get_report_types())
        .filter(parent__name='STATISTICS')[offset:limit + offset]
    )


def get_report_type_by_id(report_type_id: int) -> ReportType:
    try:
        return ReportType.objects.get(id=report_type_id)
    except ReportType.DoesNotExist:
        raise NotFoundError('Report type by ID is not found')
