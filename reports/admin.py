from django.contrib import admin
from django.conf import settings

from reports.models import ReportType, ReportRoute
from core.mixins import OnlyDebugAddChangeDeleteMixin


@admin.register(ReportType)
class ReportTypeAdmin(OnlyDebugAddChangeDeleteMixin, admin.ModelAdmin):
    def get_exclude(self, request, obj=None):
        if not settings.DEBUG:
            return 'parent', 'is_active'


@admin.register(ReportRoute)
class ReportRouteAdmin(admin.ModelAdmin):
    pass
