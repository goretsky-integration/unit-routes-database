from django.contrib import admin

from snapshots.models import DodoIsApiResponseSnapshot


@admin.register(DodoIsApiResponseSnapshot)
class DodoIsApiResponseSnapshotAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
