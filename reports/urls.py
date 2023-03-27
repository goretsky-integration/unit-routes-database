from django.urls import path

from reports.views import ReportTypesListApi, StatisticsReportTypesListApi

urlpatterns = [
    path('', ReportTypesListApi.as_view()),
    path('statistics/', StatisticsReportTypesListApi.as_view()),
]
