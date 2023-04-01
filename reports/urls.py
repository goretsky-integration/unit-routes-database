from django.urls import path

from reports.views.report_routes import (
    ReportRoutesChatIdsListApi,
    ReportRoutesCreateDeleteApi,
    ReportRoutesUnitsListApi,
)
from reports.views.report_types import (
    ReportTypesListApi,
    RetrieveReportTypeByNameApi,
    StatisticsReportTypesListApi,
)

urlpatterns = [
    path('report-types/', ReportTypesListApi.as_view()),
    path('report-types/names/<str:report_type_name>/',
         RetrieveReportTypeByNameApi.as_view()),
    path('report-types/statistics/', StatisticsReportTypesListApi.as_view()),
    path('report-routes/', ReportRoutesCreateDeleteApi.as_view()),
    path('report-routes/units/', ReportRoutesUnitsListApi.as_view()),
    path('report-routes/telegram-chats/', ReportRoutesChatIdsListApi.as_view()),
]
