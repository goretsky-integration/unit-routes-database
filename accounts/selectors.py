from django.db.models import QuerySet

from accounts.exceptions import AccountNotFoundError
from accounts.models import Account

__all__ = ('get_account_by_name', 'get_accounts', 'get_office_manager_accounts')


def get_account_by_name(name: str) -> Account:
    try:
        return Account.objects.get(name=name)
    except Account.DoesNotExist:
        raise AccountNotFoundError


def get_accounts() -> list[dict]:
    return Account.objects.values('name', 'login', 'password')


def get_office_manager_accounts() -> QuerySet[Account]:
    return Account.objects.filter(name__startswith='office_manager').all()
