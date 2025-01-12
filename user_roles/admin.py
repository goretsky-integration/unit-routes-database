from django.contrib import admin
from django.db.models import Q
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from reports.models.report_types import ReportType
from user_roles.models import UserRole


class UserRoleResource(ModelResource):
    class Meta:
        model = UserRole


@admin.register(UserRole)
class UserRoleAdmin(ImportExportModelAdmin):
    resource_class = UserRoleResource
    filter_horizontal = ('units', 'report_types')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'report_types':
            kwargs['queryset'] = ReportType.objects.exclude(
                Q(parent__name='STATISTICS') | Q(is_active=False)
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)
