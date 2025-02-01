from django.db.models import QuerySet

from accounts.exceptions import AccountNotFoundError
from accounts.models import Account, AccountCookies

__all__ = ('get_account_by_name', 'get_accounts',)


def get_account_by_name(name: str) -> Account:
    try:
        return Account.objects.get(name=name)
    except Account.DoesNotExist:
        raise AccountNotFoundError


def get_accounts() -> list[dict]:
    return [
        {
            'name': account_name,
            'login': '',
            'password': '',
        }
        for account_name in
        AccountCookies.objects.values_list('name', flat=True)
    ]
