from django.conf import settings
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from core.mixins import OnlyDebugAddChangeDeleteMixin
from reports.models.report_routes import ReportRoute
from reports.models.report_types import ReportType
from reports.models.inventory_stocks import InventoryStocks


@admin.register(InventoryStocks)
class InventoryStocksAdmin(admin.ModelAdmin):
    pass


class CategoryParentListFilter(SimpleListFilter):
    title = capfirst(_('reports|admin|filter|title'))
    parameter_name = 'report_type_without_parent'

    def lookups(self, request, model_admin):
        return (
            (
                'report_types',
                capfirst(_('reports|admin|filter|report_type')),
            ),
            (
                'statistics_report_types',
                capfirst(_('reports|admin|filter|statistics_report_type')),
            ),
        )

    def queryset(self, request, queryset):
        if self.value() == 'report_types':
            return queryset.filter(parent=None)
        elif self.value() == 'statistics_report_types':
            return queryset.exclude(parent=None)
        return queryset


def activate(modeladmin, request, queryset):
    queryset.update(is_active=True)


def deactivate(modeladmin, request, queryset):
    queryset.update(is_active=False)


class ReportTypeResource(ModelResource):
    class Meta:
        model = ReportType


@admin.register(ReportType)
class ReportTypeAdmin(OnlyDebugAddChangeDeleteMixin, ImportExportModelAdmin):
    resource_class = ReportTypeResource
    actions = (activate, deactivate)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not settings.DEBUG:
            del actions['activate']
            del actions['deactivate']
        return actions

    def get_list_filter(self, request):
        list_filter = [CategoryParentListFilter]
        if settings.DEBUG:
            list_filter.append('is_active')
        return list_filter

    def get_exclude(self, request, obj=None):
        if not settings.DEBUG:
            return 'is_active', 'name', 'id'

    def get_queryset(self, request):
        report_types = ReportType.objects.all()
        if not settings.DEBUG:
            report_types = report_types.filter(is_active=True)
        return report_types


class ReportRouteResource(ModelResource):
    class Meta:
        model = ReportRoute


@admin.register(ReportRoute)
class ReportRouteAdmin(ImportExportModelAdmin):
    resource_class = ReportRouteResource
    list_filter = ('telegram_chat', 'unit', 'report_type')
    list_select_related = ('telegram_chat', 'unit', 'report_type')
    list_display = ('telegram_chat', 'unit', 'report_type')
