from django.contrib import admin
from django.db.models import Q

from reports.models.report_types import ReportType
from user_roles.models import UserRole


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    filter_horizontal = ('units', 'report_types')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'report_types':
            kwargs['queryset'] = ReportType.objects.exclude(
                Q(parent__name='STATISTICS') | Q(is_active=False)
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)
