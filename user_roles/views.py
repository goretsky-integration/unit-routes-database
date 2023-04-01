from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import PermissionDeniedError
from telegram.selectors import get_telegram_chat_by_chat_id
from units.models import Region
from user_roles.selectors import get_role
from user_roles.services import update_user_role


class SetUserRoleApi(APIView):

    class InputSerializer(serializers.Serializer):
        access_code = serializers.CharField(max_length=64, min_length=1)

    def patch(self, request: Request, chat_id: int):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data
        access_code: str = serialized_data['access_code']

        user = get_telegram_chat_by_chat_id(chat_id)
        role = get_role(access_code)
        update_user_role(user=user, role=role)

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRoleUnitsListApi(APIView):

    def get(self, request: Request, chat_id: int):
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))
        region_id = request.query_params.get('region_id')
        if region_id is not None:
            region_id = int(region_id)

        chat = get_telegram_chat_by_chat_id(chat_id)
        if chat.role is None:
            raise PermissionDeniedError('User has no any role')

        units = chat.role.units
        if region_id is not None:
            units = units.filter(region_id=region_id)
        units = (
            units.order_by('id')[offset:limit + 1 + offset]
            .values('id', 'name', 'uuid', 'region_id',
                    'office_manager_account_name', 'dodo_is_api_account_name')
        )
        is_next_page_exists = len(units) == limit + 1
        if is_next_page_exists:
            units = units[:limit]
        response_data = {
            'units': units,
            'is_end_of_list_reached': not is_next_page_exists,
        }
        return Response(response_data)


class UserRoleRegionsListApi(APIView):

    def get(self, request: Request, chat_id: int):
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))

        chat = get_telegram_chat_by_chat_id(chat_id)
        if chat.role is None:
            raise PermissionDeniedError('User has no any role')
        region_ids = (
            chat.role.units
            .order_by('region_id')
            .distinct('region_id')
            .values_list('region_id', flat=True)
        )
        regions = (
            Region.objects
            .filter(id__in=region_ids)[offset:limit + 1 + offset]
            .values('id', 'name')
        )
        is_next_page_exists = len(regions) == limit + 1
        if is_next_page_exists:
            regions = regions[:limit]
        response_data = {
            'regions': regions,
            'is_end_of_list_reached': not is_next_page_exists,
        }
        return Response(response_data)


class UserRoleReportTypesListApi(APIView):

    def get(self, request: Request, chat_id: int):
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))

        chat = get_telegram_chat_by_chat_id(chat_id)
        if chat.role is None:
            raise PermissionDeniedError('User has no any role')

        report_types = (
            chat.role
            .report_types
            .order_by('id')[offset:limit + 1 + offset]
            .values('id', 'name', 'verbose_name')
        )
        is_next_page_exists = len(report_types) == limit + 1
        if is_next_page_exists:
            report_types = report_types[:limit]

        response_data = {
            'report_types': report_types,
            'is_end_of_list_reached': not is_next_page_exists,
        }
        return Response(response_data)
