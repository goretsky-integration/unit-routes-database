from django.contrib import admin
from import_export.admin import ExportMixin

from core.mixins import OnlyDebugAddChangeDeleteMixin
from units.forms import UnitWithIdForm
from units.models import Region, Unit, Department


class UnitInline(admin.TabularInline):
    model = Unit


@admin.register(Department)
class DepartmentAdmin(OnlyDebugAddChangeDeleteMixin, admin.ModelAdmin):
    inlines = (UnitInline,)


@admin.register(Region)
class RegionAdmin(OnlyDebugAddChangeDeleteMixin, admin.ModelAdmin):
    inlines = (UnitInline,)


@admin.register(Unit)
class UnitAdmin(OnlyDebugAddChangeDeleteMixin, ExportMixin, admin.ModelAdmin):
    form = UnitWithIdForm
    list_filter = (
        'region',
        'department',
    )
    list_select_related = ('region', 'department')
    list_display = ('name', 'region', 'department')
