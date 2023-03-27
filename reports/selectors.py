from django.db.models import QuerySet

from core.exceptions import NotFoundError
from reports.models import ReportType


def get_report_types() -> QuerySet[ReportType]:
    return ReportType.objects.all()


def get_report_type_by_id(report_type_id: int) -> ReportType:
    try:
        return ReportType.objects.get(id=report_type_id)
    except ReportType.DoesNotExist:
        raise NotFoundError('Report type by ID is not found')
