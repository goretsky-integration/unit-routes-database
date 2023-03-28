from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import PermissionDeniedError
from reports.models.report_routes import ReportRoute
from reports.selectors import get_report_routes, get_report_type_by_id
from reports.services import create_report_routes, delete_report_routes
from telegram.selectors import get_telegram_chat_by_chat_id


class ReportRoutesCreateDeleteListApi(APIView):

    class InputSerializer(serializers.Serializer):
        report_type_id = serializers.IntegerField()
        chat_id = serializers.IntegerField()
        unit_ids = serializers.ListSerializer(child=serializers.IntegerField())

    def get(self, request: Request):
        chat_id: int | None = request.query_params.get('chat_id')
        report_type_id: int | None = request.query_params.get('report_type')

        report_routes = (
            get_report_routes(
                chat_id=chat_id,
                report_type_id=report_type_id,
            )
            .values('telegram_chat__chat_id', 'report_type', 'unit_id')
        )
        return Response(report_routes)

    def post(self, request: Request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        telegram_chat = get_telegram_chat_by_chat_id(serialized_data['chat_id'])
        report_type = get_report_type_by_id(serialized_data['report_type_id'])

        report_scope = telegram_chat.report_scope

        has_access_to_report_type = report_scope.report_types.contains(
            report_type)

        if not has_access_to_report_type:
            raise PermissionDeniedError('Permission to report type denied')

        unit_ids_with_access: set[int] = {
            unit_id for unit_id in serialized_data['unit_ids']
            if report_scope.units.contains(unit_id)
        }
        permission_denied_units = (
                set(serialized_data['unit_ids']) - unit_ids_with_access)
        if not unit_ids_with_access:
            raise PermissionDeniedError('Permission to all units denied')

        create_report_routes(
            telegram_chat_id=telegram_chat.id,
            report_type_id=report_type.id,
            unit_ids=unit_ids_with_access,
        )

        response_data = {
            'permission_denied_units': permission_denied_units,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def delete(self, request: Request):
        chat_id = request.query_params['chat_id']
        report_type_id = request.query_params['report_type_id']
        unit_ids = tuple(map(int, request.query_params.getlist('unit_ids')))

        delete_report_routes(
            chat_id=chat_id,
            report_type_id=report_type_id,
            unit_ids=unit_ids,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TelegramChatIdsListApi(APIView):

    def get(self, request: Request, unit_id: int, report_type_id: int):
        response_data = (
            ReportRoute.objects
            .select_related('telegram_chat')
            .filter(unit_id=unit_id, report_type_id=report_type_id)
            .values_list('telegram_chat__chat_id', flat=True)
        )
        return Response(response_data)
