from django.contrib import admin

from core.mixins import OnlyDebugAddChangeDeleteMixin
from units.forms import UnitWithIdForm
from units.models import Region, Unit


class UnitInline(admin.TabularInline):
    model = Unit


@admin.register(Region)
class RegionAdmin(OnlyDebugAddChangeDeleteMixin, admin.ModelAdmin):
    inlines = (UnitInline,)


@admin.register(Unit)
class UnitAdmin(OnlyDebugAddChangeDeleteMixin, admin.ModelAdmin):
    form = UnitWithIdForm
    list_filter = ('region',)
