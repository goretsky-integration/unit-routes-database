from django.urls import path

from reports.views.report_routes import (
    TelegramChatIdsListApi,
    ReportRoutesCreateDeleteListApi
)
from reports.views.report_types import (
    ReportTypesListApi,
    StatisticsReportTypesListApi,
)

urlpatterns = [
    path('report-types/', ReportTypesListApi.as_view()),
    path('report-types/statistics/', StatisticsReportTypesListApi.as_view()),
    path('reports/', ReportRoutesCreateDeleteListApi.as_view()),
    path('reports/telegram-chats/', TelegramChatIdsListApi.as_view()),
]
