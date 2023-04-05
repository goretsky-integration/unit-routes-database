from django.contrib import admin
from import_export import resources
from import_export.admin import ExportMixin

from core.mixins import OnlyDebugAddChangeDeleteMixin
from units.forms import UnitWithIdForm
from units.models import Region, Unit


class UnitInline(admin.TabularInline):
    model = Unit


@admin.register(Region)
class RegionAdmin(OnlyDebugAddChangeDeleteMixin, admin.ModelAdmin):
    inlines = (UnitInline,)


@admin.register(Unit)
class UnitAdmin(OnlyDebugAddChangeDeleteMixin, ExportMixin, admin.ModelAdmin):
    form = UnitWithIdForm
    list_filter = (
        'region',
        'office_manager_account_name',
        'dodo_is_api_account_name',
    )
    list_select_related = ('region',)
    list_display = ('name', 'region')
