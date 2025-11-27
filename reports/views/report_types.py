from rest_framework import serializers
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.models.report_types import ReportType
from reports.selectors import (
    get_report_type_by_name,
)


class ReportTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportType
        fields = ('id', 'name', 'verbose_name')


class ReportTypeListApi(ListAPIView):
    serializer_class = ReportTypeSerializer
    queryset = ReportType.objects.order_by('-priority').filter(is_active=True)

    def get_queryset(self):
        queryset = super().get_queryset()
        parent_id = self.request.query_params.get("parent_id")
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        return queryset


class RetrieveReportTypeByNameApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = ReportType
            fields = ('id', 'name', 'verbose_name')

    def get(self, request: Request, report_type_name: str):
        report_type = get_report_type_by_name(report_type_name)
        return Response(self.OutputSerializer(report_type).data)
