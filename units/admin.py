from django.contrib import admin
from django.conf import settings

from units.models import Region, Unit
from units.forms import UnitWithIdForm


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return settings.DEBUG

    def has_change_permission(self, request, obj=None):
        return settings.DEBUG

    def has_delete_permission(self, request, obj=None):
        return settings.DEBUG


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    form = UnitWithIdForm

    def has_add_permission(self, request):
        return settings.DEBUG

    def has_change_permission(self, request, obj=None):
        return settings.DEBUG

    def has_delete_permission(self, request, obj=None):
        return settings.DEBUG
