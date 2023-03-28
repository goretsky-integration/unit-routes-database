from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.selectors import (
    get_active_report_types,
    get_active_statistics_report_types,
)


class ReportTypesListApi(APIView):

    def get(self, request: Request):
        report_types = get_active_report_types()
        response_data = report_types.values('id', 'name', 'verbose_name')
        return Response(response_data)


class StatisticsReportTypesListApi(APIView):

    def get(self, request: Request):
        report_types = get_active_statistics_report_types()
        response_data = report_types.values('id', 'name', 'verbose_name')
        return Response(response_data)
