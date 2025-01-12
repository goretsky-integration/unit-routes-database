from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from core.mixins import OnlyDebugAddChangeDeleteMixin
from units.forms import UnitWithIdForm
from units.models import Region, Unit, Department


class UnitResource(ModelResource):
    class Meta:
        model = Unit


class RegionResource(ModelResource):
    class Meta:
        model = Region


class DepartmentResource(ModelResource):
    class Meta:
        model = Department


class UnitInline(admin.TabularInline):
    model = Unit


@admin.register(Department)
class DepartmentAdmin(OnlyDebugAddChangeDeleteMixin, ImportExportModelAdmin):
    resource_class = DepartmentResource
    inlines = (UnitInline,)


@admin.register(Region)
class RegionAdmin(OnlyDebugAddChangeDeleteMixin, ImportExportModelAdmin):
    resource_class = RegionResource
    inlines = (UnitInline,)


@admin.register(Unit)
class UnitAdmin(OnlyDebugAddChangeDeleteMixin, ImportExportModelAdmin):
    resource_class = UnitResource
    form = UnitWithIdForm
    list_filter = (
        'region',
        'department',
    )
    list_select_related = ('region', 'department')
    list_display = ('name', 'region', 'department')
