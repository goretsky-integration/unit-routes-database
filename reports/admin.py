from django.contrib import admin

from reports.models import ReportType, ReportRoute


@admin.register(ReportType)
class ReportTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(ReportRoute)
class ReportRouteAdmin(admin.ModelAdmin):
    pass
