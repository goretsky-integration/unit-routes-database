from typing import TypedDict

from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.use_cases.create_awaiting_orders_report import \
    CreateAwaitingOrdersReportUseCase
from reports.use_cases.create_cooking_time_report import \
    (
    CreateDeliveryCookingTimeReportUseCase,
    CreateRestaurantCookingTimeReportUseCase,
)
from reports.use_cases.create_daily_revenue_report import \
    CreateDailyRevenueReportUseCase
from reports.use_cases.create_delivery_performance_report import \
    CreateDeliveryPerformanceReportUseCase
from reports.use_cases.create_delivery_speed_report import \
    CreateDeliverySpeedReportUseCase
from reports.use_cases.create_heated_shelf_statistics_report import \
    CreateHeatedShelfStatisticsReport
from reports.use_cases.create_kitchen_performance_report import \
    CreateKitchenPerformanceReportUseCase
from reports.use_cases.create_late_delivery_vouchers_report import \
    CreateLateDeliveryVouchersReportUseCase
from reports.use_cases.create_productivity_balance_report import \
    CreateProductivityBalanceReportUseCase


class ReportCreateInputSerializer(serializers.Serializer):
    report_type_id = serializers.IntegerField()
    chat_id = serializers.IntegerField()


class RequestData(TypedDict):
    report_type_id: int
    chat_id: int


class ReportCreateApi(APIView):

    def post(self, request: Request) -> Response:
        serializer = ReportCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: RequestData = serializer.data

        report_type_id = int(serialized_data['report_type_id'])

        if report_type_id == 17:
            CreateDailyRevenueReportUseCase(
                chat_id=serialized_data['chat_id'],
            ).execute()
        elif report_type_id == 10:
            CreateDeliveryCookingTimeReportUseCase(
                chat_id=serialized_data['chat_id'],
            ).execute()
        elif report_type_id == 11:
            CreateRestaurantCookingTimeReportUseCase(
                chat_id=serialized_data['chat_id'],
            ).execute()
        elif report_type_id == 12:
            CreateKitchenPerformanceReportUseCase(
                chat_id=serialized_data['chat_id'],
            ).execute()
        elif report_type_id == 13:
            CreateHeatedShelfStatisticsReport(
                chat_id=serialized_data['chat_id'],
            ).execute()
        elif report_type_id == 14:
            CreateDeliverySpeedReportUseCase(
                chat_id=serialized_data['chat_id'],
            ).execute()
        elif report_type_id == 15:
            CreateDeliveryPerformanceReportUseCase(
                chat_id=serialized_data['chat_id'],
            ).execute()
        elif report_type_id == 16:
            CreateLateDeliveryVouchersReportUseCase(
                chat_id=serialized_data['chat_id'],
            ).execute()
        elif report_type_id == 18:
            CreateAwaitingOrdersReportUseCase(
                chat_id=serialized_data['chat_id'],
            ).execute()
        elif report_type_id == 20:
            CreateProductivityBalanceReportUseCase(
                chat_id=serialized_data['chat_id'],
            ).execute()

        return Response(status=status.HTTP_202_ACCEPTED)
