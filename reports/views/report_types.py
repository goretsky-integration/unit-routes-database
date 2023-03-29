from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.selectors import (
    get_active_report_types,
    get_active_statistics_report_types,
)


class ReportTypesListApi(APIView):

    def get(self, request: Request):
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))
        report_types = get_active_report_types(limit=limit, offset=offset)
        is_next_page_exists = get_active_report_types(
            limit=1,
            offset=limit + offset,
        ).exists()
        response_data = {
            'report_types': report_types.values('id', 'name', 'verbose_name'),
            'is_end_of_list_reached': not is_next_page_exists,
        }
        return Response(response_data)


class StatisticsReportTypesListApi(APIView):

    def get(self, request: Request):
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))
        report_types = get_active_statistics_report_types(
            limit=limit,
            offset=offset,
        )
        is_next_page_exists = get_active_statistics_report_types(
            limit=1,
            offset=limit + offset,
        ).exists()
        response_data = {
            'report_types': report_types.values('id', 'name', 'verbose_name'),
            'is_end_of_list_reached': not is_next_page_exists,
        }
        return Response(response_data)
