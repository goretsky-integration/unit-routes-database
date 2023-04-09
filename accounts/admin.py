from django.contrib import admin
from django.conf import settings

from accounts.models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):

    def get_fields(self, request, obj=None):
        fields = ['name']
        if settings.DEBUG:
            fields += ['login', 'password']
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if not settings.DEBUG:
            readonly_fields.append('name')
        return readonly_fields
