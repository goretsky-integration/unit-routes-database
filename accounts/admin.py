from django.contrib import admin

from accounts.models import Account, AccountCookies, AccountTokens


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass


@admin.register(AccountCookies)
class AccountCookiesAdmin(admin.ModelAdmin):
    pass


@admin.register(AccountTokens)
class AccountTokensAdmin(admin.ModelAdmin):
    pass
