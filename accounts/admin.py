from django.contrib import admin

from accounts.models import (
    Account,
    DodoISAPICredentials,
    DodoISSessionCredentials,
)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass


@admin.register(DodoISAPICredentials)
class DodoISAPICredentialsAdmin(admin.ModelAdmin):
    pass


@admin.register(DodoISSessionCredentials)
class DodoISSessionCredentialsAdmin(admin.ModelAdmin):
    pass
