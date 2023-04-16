from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers import LimitOffsetSerializer
from reports.models.report_types import ReportType
from reports.selectors import (
    get_active_report_types,
    get_active_statistics_report_types,
    get_report_type_by_name,
)


class ReportTypesListApi(APIView):

    def get(self, request: Request):
        serializer = LimitOffsetSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        limit: int = serialized_data['limit']
        offset: int = serialized_data['offset']

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
        serializer = LimitOffsetSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        limit: int = serialized_data['limit']
        offset: int = serialized_data['offset']

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


class RetrieveReportTypeByNameApi(APIView):

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = ReportType
            fields = ('id', 'name', 'verbose_name')

    def get(self, request: Request, report_type_name: str):
        report_type = get_report_type_by_name(report_type_name)
        return Response(self.OutputSerializer(report_type).data)
