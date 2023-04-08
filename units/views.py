from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request

from units.models import Unit, Department
from units.selectors import (
    get_regions, get_units, get_unit_by_name,
    get_departments_by_unit_office_manager_account_name
)


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
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('skip', 0))
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
                    'office_manager_account_name': unit['office_manager_account_name'],
                    'dodo_is_api_account_name': unit['dodo_is_api_account_name'],
                    'region': unit['region__name'],
                } for unit in units
            ],
            'is_end_of_list_reached': not is_next_page_exists,
        }
        return Response(response_data)


class UnitRegionsListApi(APIView):

    def get(self, request):
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))
        regions = get_regions(limit=limit, offset=offset)
        is_next_page_exists = get_regions(
            limit=1,
            offset=limit + offset,
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
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))
        office_manager_account_name: str = request.query_params['office_manager_account_name']
        departments = get_departments_by_unit_office_manager_account_name(
            office_manager_account_name=office_manager_account_name,
            limit=limit + 1,
            offset=offset,
        ).values('id', 'name', 'uuid')

        is_end_of_list_reached = len(departments) < limit + 1
        response_data = {
            'departments': departments[:limit],
            'is_end_of_list_reached': is_end_of_list_reached,
        }
        return Response(response_data)
