from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from accounts.models import Account, AccountCookies, AccountTokens


class AccountResource(ModelResource):
    class Meta:
        model = Account


class AccountCookiesResource(ModelResource):
    class Meta:
        model = AccountCookies


class AccountTokensResource(ModelResource):
    class Meta:
        model = AccountTokens


@admin.register(Account)
class AccountAdmin(ImportExportModelAdmin):
    resource_class = AccountResource


@admin.register(AccountCookies)
class AccountCookiesAdmin(ImportExportModelAdmin):
    resource_class = AccountCookiesResource


@admin.register(AccountTokens)
class AccountTokensAdmin(ImportExportModelAdmin):
    resource_class = AccountTokensResource
