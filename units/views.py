from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from core.serializers import LimitOffsetSerializer
from units.models import Department, Unit
from units.selectors import get_units, get_unit_by_name


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

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        uuid = serializers.UUIDField()
        office_manager_account_name = serializers.CharField(
            source='office_manager_account.name',
            allow_null=True,
        )
        dodo_is_api_account_name = serializers.CharField(
            source='dodo_is_api_account.name',
            allow_null=True,
        )
        region = serializers.CharField(
            source='region.name',
            allow_null=True,
        )

    def get(self, request):
        serializer = LimitOffsetSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        limit: int = serialized_data['limit']
        offset: int = serialized_data['offset']

        units = (
            Unit.objects
            .select_related('region')
            .only('id', 'name', 'uuid', 'office_manager_account__name',
                  'dodo_is_api_account__name', 'shift_manager_account__name',
                  'region__name')
        )[offset:offset + limit + 1]
        print(units.query)

        serializer = self.OutputSerializer(units, many=True)
        response_data = {
            'units': serializer.data,
            'is_end_of_list_reached': True,
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
