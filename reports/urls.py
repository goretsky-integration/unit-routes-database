from django.urls import path

from reports.views.report_create import ReportCreateApi
from reports.views.report_routes import (
    ReportRoutesChatIdsListApi,
    ReportRoutesCreateDeleteApi,
    ReportRoutesUnitsListApi,
)
from reports.views.report_types import (
    RetrieveReportTypeByNameApi,
    ReportTypeListApi,
)


urlpatterns = [
    path('reports/', ReportCreateApi.as_view()),
    path('report-types/', ReportTypeListApi.as_view()),
    path(
        'report-types/names/<str:report_type_name>/',
        RetrieveReportTypeByNameApi.as_view(),
    ),
    path('report-routes/', ReportRoutesCreateDeleteApi.as_view()),
    path('report-routes/units/', ReportRoutesUnitsListApi.as_view()),
    path(
        'report-routes/telegram-chats/', ReportRoutesChatIdsListApi.as_view(),
    ),
]
