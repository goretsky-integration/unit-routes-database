from django.conf import settings
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

from core.mixins import OnlyDebugAddChangeDeleteMixin
from reports.models.report_routes import ReportRoute
from reports.models.report_types import ReportType


class CategoryParentListFilter(SimpleListFilter):
    title = _('Report types')
    parameter_name = 'report_type_without_parent'

    def lookups(self, request, model_admin):
        return (
            ('report_types', _('Report types')),
            ('statistics_report_types', _('Statistics report types')),
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


@admin.register(ReportType)
class ReportTypeAdmin(OnlyDebugAddChangeDeleteMixin, admin.ModelAdmin):
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
            return 'parent', 'is_active'


@admin.register(ReportRoute)
class ReportRouteAdmin(admin.ModelAdmin):
    pass
