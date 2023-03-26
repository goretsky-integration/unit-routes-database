from rest_framework.response import Response
from rest_framework.views import APIView

from units.selectors import get_region_names, get_units, get_unit_by_name


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
        limit = request.query_params.get('limit', 100)
        offset = request.query_params.get('skip', 0)
        units = get_units(limit=limit, offset=offset)
        response_data = [
            {
                'id': unit.id,
                'name': unit.name,
                'uuid': unit.uuid,
                'office_manager_account_name': unit.office_manager_account_name,
                'dodo_is_api_account_name': unit.dodo_is_api_account_name,
                'region': unit.region.name,
            } for unit in units
        ]
        return Response(response_data)


class UnitRegionsListApi(APIView):

    def get(self, request):
        response_data = get_region_names()
        return Response(response_data)
