from django.contrib import admin

from accounts.models import (
    Account,
    DodoISAPICredentials,
    OfficeManagerSessionCredentials,
    ShiftManagerSessionCredentials,
)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass


@admin.register(DodoISAPICredentials)
class DodoISAPICredentialsAdmin(admin.ModelAdmin):
    pass


@admin.register(OfficeManagerSessionCredentials)
class OfficeManagerSessionCredentialsAdmin(admin.ModelAdmin):
    pass


@admin.register(ShiftManagerSessionCredentials)
class ShiftManagerSessionCredentialsAdmin(admin.ModelAdmin):
    pass
