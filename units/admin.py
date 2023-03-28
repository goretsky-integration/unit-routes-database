from django.conf import settings
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from core.mixins import OnlyDebugAddChangeDeleteMixin
from units.forms import UnitWithIdForm
from units.models import Region, Unit

ModelAdmin = ImportExportModelAdmin if settings.DEBUG else admin.ModelAdmin


class UnitResource(resources.ModelResource):
    class Meta:
        model = Unit


class UnitInline(admin.TabularInline):
    model = Unit


@admin.register(Region)
class RegionAdmin(OnlyDebugAddChangeDeleteMixin, admin.ModelAdmin):
    inlines = (UnitInline,)


@admin.register(Unit)
class UnitAdmin(OnlyDebugAddChangeDeleteMixin, ModelAdmin):
    form = UnitWithIdForm
    list_filter = ('region',)

    if settings.DEBUG:
        resource_class = UnitResource
