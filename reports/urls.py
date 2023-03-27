from django.urls import path

from reports.views import (
    ReportTypesListApi,
    StatisticsReportTypesListApi,
)

urlpatterns = [
    path('report-types/', ReportTypesListApi.as_view()),
    path('report-types/statistics/', StatisticsReportTypesListApi.as_view()),
]
