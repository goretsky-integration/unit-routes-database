from django.conf import settings
from django.contrib import admin
from import_export.admin import ExportMixin, ImportExportModelAdmin

from core.mixins import OnlyDebugAddChangeDeleteMixin
from units.forms import UnitWithIdForm
from units.models import Unit, Department

if settings.DEBUG:
    class ModelAdmin(ImportExportModelAdmin):
        pass
else:
    class ModelAdmin(ExportMixin, admin.ModelAdmin):
        pass


class UnitInline(admin.TabularInline):
    model = Unit


@admin.register(Department)
class DepartmentAdmin(OnlyDebugAddChangeDeleteMixin, ModelAdmin):
    inlines = (UnitInline,)


@admin.register(Unit)
class UnitAdmin(OnlyDebugAddChangeDeleteMixin, ModelAdmin):
    form = UnitWithIdForm
    list_filter = ('department',)
    list_select_related = ('department',)
    list_display = ('name', 'department')
