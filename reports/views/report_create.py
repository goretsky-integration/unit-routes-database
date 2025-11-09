from typing import TypedDict

from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.use_cases.create_daily_revenue_report import \
    CreateDailyRevenueReportUseCase


class ReportCreateInputSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=['DAILY_REVENUE'])
    chat_id = serializers.IntegerField()


class RequestData(TypedDict):
    report_type: str
    chat_id: int


class ReportCreateApi(APIView):

    def post(self, request: Request) -> Response:
        serializer = ReportCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: RequestData = serializer.data

        if serialized_data['report_type'] == 'DAILY_REVENUE':
            CreateDailyRevenueReportUseCase(
                chat_id=serialized_data['chat_id'],
            ).execute()

        return Response(status=status.HTTP_202_ACCEPTED)
