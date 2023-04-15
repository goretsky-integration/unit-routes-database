from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers import LimitOffsetSerializer
from units.models import Department
from units.selectors import get_regions, get_units, get_unit_by_name


class UnitRetrieveByNameApi(APIView):

    def get(self, request, unit_name: str):
        unit = get_unit_by_name(unit_name)
        response_data = {
            'id': unit.id,
            'name': unit.name,
            'uuid': unit.uuid,
            'office_manager_account_name': unit.office_manager_account_name,
            'dodo_is_api_account_name': unit.dodo_is_api_account_name,
            'region': unit.region.name,
        }
        return Response(response_data)


class UnitsListApi(APIView):

    def get(self, request):
        serializer = LimitOffsetSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        limit: int = serialized_data['limit']
        offset: int = serialized_data['offset']

        units = (
            get_units(limit=limit, offset=offset)
            .values('id', 'name', 'uuid', 'office_manager_account_name',
                    'dodo_is_api_account_name', 'region__name')
        )
        is_next_page_exists = get_units(limit=1, offset=limit + offset).exists()
        response_data = {
            'units': [
                {
                    'id': unit['id'],
                    'name': unit['name'],
                    'uuid': unit['uuid'],
                    'office_manager_account_name': unit[
                        'office_manager_account_name'],
                    'dodo_is_api_account_name': unit[
                        'dodo_is_api_account_name'],
                    'region': unit['region__name'],
                } for unit in units
            ],
            'is_end_of_list_reached': not is_next_page_exists,
        }
        return Response(response_data)


class UnitRegionsListApi(APIView):

    def get(self, request):
        serializer = LimitOffsetSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        regions = get_regions(
            limit=serialized_data['limit'],
            offset=serialized_data['offset'],
        )
        is_next_page_exists = get_regions(
            limit=1,
            offset=serialized_data['limit'] + serialized_data['offset'],
        ).exists()
        response_data = {
            'regions': [
                {
                    'id': region.id,
                    'name': region.name,
                } for region in regions
            ],
            'is_end_of_list_reached': not is_next_page_exists,
        }
        return Response(response_data)


class UnitDepartmentsListApi(APIView):

    def get(self, request: Request):
        serializer = LimitOffsetSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        limit: int = serialized_data['limit']
        offset: int = serialized_data['offset']

        departments = (
            Department.objects.all()[offset:offset + limit + 1]
            .values('id', 'name', 'uuid')
        )

        is_end_of_list_reached = len(departments) < limit + 1
        response_data = {
            'departments': departments[:limit],
            'is_end_of_list_reached': is_end_of_list_reached,
        }
        return Response(response_data)
