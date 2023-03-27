from django.db.models import QuerySet

from reports.models import ReportType


def get_report_types() -> QuerySet[ReportType]:
    return ReportType.objects.all()
